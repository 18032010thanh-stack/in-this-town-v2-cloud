#!/usr/bin/env python3
"""Blender/GitHub visual review loop runner. Never chooses a project's visual style."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".render-loop"


def run(args: list[str], **kwargs):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, check=True, **kwargs)


def get_project(slug: str):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", slug):
        raise ValueError("Slug must be 2-63 lower-case letters, digits or hyphens")
    project = ROOT / "projects" / slug
    script = project / "render-preview.sh"
    if not script.is_file():
        raise FileNotFoundError(
            f"Missing {script}. Each NEW project must supply its own native Blender preview script."
        )
    if script.is_symlink() or project.is_symlink():
        raise ValueError("Symlinked project or script not allowed")
    return project, script


def render(slug: str, round_number: int):
    project, script = get_project(slug)
    if not 0 <= round_number <= 2:
        raise ValueError("Only 3 bounded preview rounds supported (0,1,2)")
    iteration = WORK / f"r{round_number}"
    iteration.mkdir(parents=True, exist_ok=True)
    video = iteration / "preview.mp4"
    if video.exists():
        video.unlink()
    env = os.environ.copy()
    env.update({
        "AUTOPILOT_PROJECT": slug,
        "AUTOPILOT_ROUND": str(round_number),
        "AUTOPILOT_OUTPUT_DIR": str(iteration),
    })
    # No model credentials or GitHub write token are injected into the Blender step.
    run(["bash", str(script)], cwd=project, env=env)
    if not video.is_file() or video.stat().st_size < 1024:
        raise ValueError(f"Project renderer did not produce a non-empty {video}")
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,codec_type,width,height,avg_frame_rate,nb_frames",
        "-of", "json", str(video)
    ], text=True))
    streams = [x for x in info.get("streams", []) if x.get("codec_type") == "video"]
    if not streams:
        raise ValueError("Preview video has no video stream")
    stream = streams[0]
    duration = float(info["format"]["duration"])
    if not (0.5 <= duration <= 30):
        raise ValueError(f"Preview should be 0.5-30 seconds, got {duration}")
    if stream.get("width", 0) < 128 or stream.get("height", 0) < 128:
        raise ValueError("Invalid image resolution")
    for i, t in enumerate((0.1, 0.5, 0.9), start=1):
        pic = iteration / f"frame_{i}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(duration*t),
             "-i", str(video), "-frames:v", "1", "-vf", "scale=480:-2",
             str(pic)])
        if not pic.is_file() or pic.stat().st_size < 500:
            raise RuntimeError(f"Could not extract preview frame {i}")
    # Use a single image file with THREE separate moments for vision review.
    strip = iteration / "review_strip.png"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(iteration/"frame_1.png"),
         "-i", str(iteration/"frame_2.png"), "-i", str(iteration/"frame_3.png"),
         "-filter_complex", "hstack=inputs=3", "-frames:v", "1", str(strip)])
    manifest = {
        "project": slug,
        "round": round_number,
        "preview_seconds": duration,
        "video": str(video.relative_to(ROOT)),
        "review_image": str(strip.relative_to(ROOT)),
        "width": stream["width"],
        "height": stream["height"],
        "fps": stream.get("avg_frame_rate"),
        "source_authority": f"projects/{slug}/ only; no other project style",
    }
    (iteration / "report.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORK / "context.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VERIFIED", json.dumps(manifest, ensure_ascii=False), flush=True)


def gate(slug: str, round_number: int):
    if round_number not in (1, 2):
        raise ValueError("Invalid gate")
    get_project(slug)
    decision = WORK / "decision.json"
    if not decision.is_file():
        raise RuntimeError("AI reviewer must write .render-loop/decision.json")
    data = json.loads(decision.read_text(encoding="utf-8"))
    if not isinstance(data.get("continue"), bool):
        raise ValueError("AI decision must contain boolean 'continue'")
    # Ensure changes are to the CURRENT project only, not past projects/workflows.
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "-z"], cwd=ROOT).decode().strip("\0").split("\0")
    changed = [p for p in changed if p]
    outside = [p for p in changed if not p.startswith(f"projects/{slug}/")]
    if outside:
        raise RuntimeError(f"Reviewer edited files outside current project: {outside}")
    if data["continue"] and not changed:
        print("AI requested rerender but made no tracked-file changes; stopping.", flush=True)
    iterate = bool(data["continue"] and changed)
    print(f"VISUAL GATE {round_number}", json.dumps(data, ensure_ascii=False),
          "changed:", changed, "continue:", iterate, flush=True)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
        out.write(f"iterate={'true' if iterate else 'false'}\n")
    (WORK / f"decision_{round_number}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    decision.unlink()


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("render")
    p.add_argument("--slug", required=True)
    p.add_argument("--round", type=int, required=True, dest="round_number")
    p = sub.add_parser("gate")
    p.add_argument("--slug", required=True)
    p.add_argument("--round", type=int, required=True, dest="round_number")
    args = parser.parse_args()
    if args.mode == "render":
        render(args.slug, args.round_number)
    else:
        gate(args.slug, args.round_number)


if __name__ == "__main__":
    main()
