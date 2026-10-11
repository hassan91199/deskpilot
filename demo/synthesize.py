#!/usr/bin/env python3
"""Synthesize narration audio and per-phrase caption timings for script.json.

Run with demo/.venv's interpreter (edge-tts + playwright live there, not in
the project's own .venv). Caches each scene's clip + word timings by
(voice, text) under demo/build/clips/ so reruns don't re-hit edge-tts.
"""

import asyncio
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import edge_tts

DEMO_DIR = Path(__file__).parent
BUILD_DIR = DEMO_DIR / "build"
CLIPS_DIR = BUILD_DIR / "clips"


def clip_paths(voice: str, text: str) -> tuple[Path, Path]:
    key = hashlib.sha256(f"{voice}|{text}".encode()).hexdigest()[:16]
    return CLIPS_DIR / f"{key}.mp3", CLIPS_DIR / f"{key}.json"


async def synthesize(voice: str, text: str, mp3_path: Path) -> list[tuple[float, float]]:
    attempt = 0
    while True:
        try:
            words: list[tuple[float, float]] = []
            comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
            with open(mp3_path, "wb") as audio:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        audio.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        start = chunk["offset"] / 1e7
                        words.append((start, start + chunk["duration"] / 1e7))
            if not words:
                raise RuntimeError("edge-tts returned no WordBoundary events")
            return words
        except Exception as exc:
            attempt += 1
            if attempt > 3:
                raise
            wait = 20 * attempt
            print(f"edge-tts failed ({exc}), retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def phrase_timings(
    phrases: list[str], words: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    timings = []
    idx = 0
    for phrase in phrases:
        n = len(phrase.split())
        phrase_words = words[idx : idx + n]
        if len(phrase_words) != n:
            raise AssertionError(
                f"word count mismatch for phrase {phrase!r}: expected {n}, got {len(phrase_words)}"
            )
        timings.append((phrase_words[0][0], phrase_words[-1][1]))
        idx += n
    if idx != len(words):
        raise AssertionError(f"leftover word events: used {idx} of {len(words)}")
    return timings


async def synthesize_scene(voice: str, scene: dict) -> dict:
    text = " ".join(scene["phrases"])
    mp3_path, timing_path = clip_paths(voice, text)
    if mp3_path.exists() and timing_path.exists():
        words = [tuple(w) for w in json.loads(timing_path.read_text())]
    else:
        words = await synthesize(voice, text, mp3_path)
        timing_path.write_text(json.dumps(words))

    duration = ffprobe_duration(mp3_path)
    timings = phrase_timings(scene["phrases"], words)
    return {
        "id": scene["id"],
        "clip": str(mp3_path.relative_to(DEMO_DIR)),
        "duration": duration,
        "phrases": [
            {"text": p, "start": s, "end": e}
            for p, (s, e) in zip(scene["phrases"], timings)
        ],
    }


async def main() -> None:
    script = json.loads((DEMO_DIR / "script.json").read_text())
    voice = script["voice"]
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    scenes_out = []
    for scene in script["scenes"]:
        out = await synthesize_scene(voice, scene)
        scenes_out.append(out)
        print(f"{out['id']}: {out['duration']:.2f}s, {len(out['phrases'])} phrases")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "narration.json").write_text(json.dumps(scenes_out, indent=2))
    total = sum(s["duration"] for s in scenes_out)
    print(f"total narration: {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
