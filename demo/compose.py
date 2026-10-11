#!/usr/bin/env python3
"""Compose demo/build/raw.webm + demo/build/narration.json + cues.json into
the final narrated, captioned docs/demo/demo.mp4 in one ffmpeg pass:
captions in a bar under the app, narration mixed in at each scene's cue
time, loudness-normalised.

Run with demo/.venv's interpreter (or system ffmpeg is enough, this script
only shells out to it - no edge-tts/playwright import needed here).
"""

import json
import subprocess
from pathlib import Path

DEMO_DIR = Path(__file__).parent
BUILD_DIR = DEMO_DIR / "build"
OUT_PATH = DEMO_DIR.parent / "docs" / "demo" / "demo.mp4"

PAD_H = 100  # caption bar height, added under the recorded app
FONT_SIZE_720 = 10  # tuned at 1440x900+pad; libass scales to a 288px-high script


def ffprobe(path: Path, stream: str) -> tuple[int, int]:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0:s=x", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    w, h = out.stdout.strip().split("x")
    return int(w), int(h)


def srt_timestamp(t: float) -> str:
    if t < 0:
        t = 0.0
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    narration = {s["id"]: s for s in json.loads((BUILD_DIR / "narration.json").read_text())}
    cues = {c["id"]: c for c in json.loads((BUILD_DIR / "cues.json").read_text())}
    script = json.loads((DEMO_DIR / "script.json").read_text())

    raw_path = BUILD_DIR / "raw.webm"
    width, height = ffprobe(raw_path, "video")
    padded_h = height + PAD_H
    font_size = round(FONT_SIZE_720 * padded_h / 1000)  # tuned at a 1000px-high reference
    margin_v = round(9 * padded_h / 1000)

    srt_lines = []
    idx = 1
    audio_inputs = []
    adelay_filters = []
    scene_ends = []
    for i, scene in enumerate(script["scenes"]):
        n = narration[scene["id"]]
        cue_start = cues[scene["id"]]["narration_start"]
        scene_ends.append(cue_start + n["duration"])

        audio_inputs += ["-i", str(DEMO_DIR / n["clip"])]
        delay_ms = max(round(cue_start * 1000), 0)
        adelay_filters.append(f"[{i + 1}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

        for phrase in n["phrases"]:
            start = cue_start + phrase["start"]
            end = cue_start + phrase["end"] + 0.25
            srt_lines.append(
                f"{idx}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{phrase['text']}\n"
            )
            idx += 1

    srt_path = BUILD_DIR / "captions.srt"
    srt_path.write_text("\n".join(srt_lines))

    total_duration = max(scene_ends) + 1.5
    n_audio = len(script["scenes"])
    mix_inputs = "".join(f"[a{i}]" for i in range(n_audio))

    filter_complex = (
        f"[0:v]pad={width}:{padded_h}:0:0:color=0x0b0d11,"
        f"subtitles={srt_path}:force_style="
        f"'FontName=DejaVu Sans,FontSize={font_size},Bold=1,"
        f"PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=0,Shadow=0,"
        f"Alignment=2,MarginV={margin_v}'[v];"
        + ";".join(adelay_filters)
        + f";{mix_inputs}amix=inputs={n_audio}:normalize=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=9[a]"
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_path),
        *audio_inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        str(OUT_PATH),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {OUT_PATH} ({total_duration:.1f}s)")


if __name__ == "__main__":
    main()
