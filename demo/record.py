#!/usr/bin/env python3
"""Record the real DeskPilot UI, paced against demo/build/narration.json's
per-scene durations. Requires the real stack already running:
  - docker compose up -d postgres (+ ingest already run)
  - API on http://localhost:8000
  - frontend (`npm run dev`) on http://localhost:3000

Writes demo/build/raw.webm and demo/build/cues.json (each scene's narration
start time on the recording's own clock, used by compose.py to place audio
and captions). Also drops a screenshot per query scene into
demo/build/shots/ for Step 3 (fresh stills) reuse.

Run with demo/.venv's interpreter.
"""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

DEMO_DIR = Path(__file__).parent
BUILD_DIR = DEMO_DIR / "build"
SHOTS_DIR = BUILD_DIR / "shots"
FRONTEND_URL = "http://localhost:3000"
LEAD_S = 0.6  # narration starts slightly before the mouse begins moving
TAIL_S = 1.0  # hold after narration + action both finish

CURSOR_INIT_SCRIPT = """
(() => {
  const dot = document.createElement('div');
  dot.style.position = 'fixed';
  dot.style.width = '14px';
  dot.style.height = '14px';
  dot.style.borderRadius = '50%';
  dot.style.background = 'rgba(220,38,38,0.85)';
  dot.style.border = '2px solid white';
  dot.style.zIndex = '2147483647';
  dot.style.pointerEvents = 'none';
  dot.style.left = '-100px';
  dot.style.top = '-100px';
  dot.style.transform = 'translate(-50%,-50%)';
  function attach() {
    if (!document.body) { requestAnimationFrame(attach); return; }
    document.body.appendChild(dot);
  }
  attach();
  window.addEventListener('mousemove', (e) => {
    dot.style.left = e.clientX + 'px';
    dot.style.top = e.clientY + 'px';
  });
})();
"""


def bubble_count(page) -> int:
    return page.evaluate("document.querySelectorAll('.rounded-lg').length")


def move_to(page, locator) -> None:
    box = locator.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(cx, cy, steps=30)


def run_query_scene(page, scene_start: float, narration_duration: float, query: str) -> dict:
    input_box = page.get_by_placeholder("Ask DeskPilot…")
    send_button = page.get_by_role("button", name="Send")

    prev_count = bubble_count(page)

    # Lead time: narration audio will be placed LEAD_S before this action
    # starts, so give the recording that same head start before moving.
    time.sleep(LEAD_S)
    action_start = time.monotonic() - scene_start

    move_to(page, input_box)
    input_box.click()
    input_box.type(query, delay=35)
    move_to(page, send_button)
    send_button.click()

    page.wait_for_function(
        "(args) => document.querySelectorAll(args.sel).length >= args.target",
        arg={"sel": ".rounded-lg", "target": prev_count + 2},
        timeout=60_000,
    )

    narration_start = action_start - LEAD_S
    target_end = narration_start + narration_duration + TAIL_S
    now = time.monotonic() - scene_start
    if target_end > now:
        time.sleep(target_end - now)

    return {"narration_start": max(narration_start, 0.0)}


def run_intro_scene(scene_start: float, narration_duration: float) -> dict:
    narration_start = time.monotonic() - scene_start
    time.sleep(narration_duration + TAIL_S)
    return {"narration_start": narration_start}


def main() -> None:
    narration = {
        s["id"]: s for s in json.loads((BUILD_DIR / "narration.json").read_text())
    }
    script = json.loads((DEMO_DIR / "script.json").read_text())

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, executable_path="/usr/bin/google-chrome"
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(BUILD_DIR),
            record_video_size={"width": 1440, "height": 900},
        )
        context.add_init_script(CURSOR_INIT_SCRIPT)
        page = context.new_page()
        # Cue clock starts the instant the page exists, same as the video's
        # own clock does - starting it earlier reads every cue late.
        scene_start = time.monotonic()

        page.goto(FRONTEND_URL)
        page.wait_for_selector("text=DeskPilot is thinking", state="hidden", timeout=5_000)
        page.get_by_placeholder("Ask DeskPilot…").wait_for(state="visible")

        cues = []
        for scene in script["scenes"]:
            n = narration[scene["id"]]
            if "query" in scene:
                result = run_query_scene(page, scene_start, n["duration"], scene["query"])
                page.screenshot(path=str(SHOTS_DIR / f"{scene['id']}.png"))
            else:
                result = run_intro_scene(scene_start, n["duration"])

            # result["narration_start"] is already elapsed time since the
            # recording began (scene_start) - not an offset to add to
            # anything, or the result below ends up roughly doubled.
            cues.append({"id": scene["id"], "narration_start": result["narration_start"]})
            print(f"{scene['id']}: narration_start={cues[-1]['narration_start']:.2f}s")

        video_path = page.video.path()
        context.close()
        browser.close()

    final_path = BUILD_DIR / "raw.webm"
    Path(video_path).rename(final_path)
    (BUILD_DIR / "cues.json").write_text(json.dumps(cues, indent=2))
    print(f"wrote {final_path}")


if __name__ == "__main__":
    main()
