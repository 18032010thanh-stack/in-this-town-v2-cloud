#!/usr/bin/env python3
"""Compare equivalent native Blender QA captures on a local Blender and GitHub runner.

No AI API key, no background agent. A per-project render-stills.sh performs the
actual scene work; this script measures it and validates three frames per shot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
SHOT = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")
LABELS = ("start", "middle", "end")


def parse_ids(csv: str) -> list[str]:
    ids = [x.strip() for x in csv.split(",") if x.strip()]
    if not ids or len(ids) > 20 or len(set(ids)) != len(ids):
        raise ValueError("Choose 1-20 unique representative shot IDs")
    if any(not SHOT.fullmatch(x) for x in ids):
        raise ValueError("Shot IDs must be safe alphanumeric slugs")
    return ids


def project_path(slug: str) -> Path:
    if not SLUG.fullmatch(slug):
        raise ValueError("Invalid project slug")
    path = ROOT / "projects" / slug
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"Missing or symlinked project: {path}")
    return path


def git_info() -> tuple[str | None, bool]:
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no", "--", "projects"],
            cwd=ROOT, stderr=subprocess.DEVNULL, text=True,
        ).strip())
        return revision, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, True


def capture(slug: str, host: str, shots: list[str], timeout: int, setup_s: float) -> dict:
    project = project_path(slug)
    script = project / "render-stills.sh"
    if not script.is_file() or script.is_symlink():
        raise ValueError(
            "Required project-specific render-stills.sh is missing. "
            "Codex must adapt the CURRENT project's Blender renderer, not borrow another."
        )
    output = ROOT / ".render-loop" / "hybrid" / host
    output.mkdir(parents=True, exist_ok=True)
    for old in output.rglob("*.png"):
        old.unlink()
    env = os.environ.copy()
    env["AUTOPILOT_OUTPUT_DIR"] = str(output)
    env["AUTOPILOT_SHOT_IDS"] = ",".join(shots)
    env["AUTOPILOT_CAPTURE_MODE"] = "qa-stills"
    env["AUTOPILOT_PROJECT"] = slug
    print("Rendering project", slug, "on", host, "shots:", shots, flush=True)
    start = time.perf_counter()
    p = subprocess.run(
        ["bash", str(script)], cwd=project, env=env, timeout=timeout,
        check=False,
    )
    elapsed = round(time.perf_counter() - start, 3)
    if p.returncode:
        raise RuntimeError(f"Native Blender capture exited {p.returncode} in {elapsed}s")
    images = []
    for shot in shots:
        for label in LABELS:
            image = output / "shots" / shot / (label + ".png")
            if not image.is_file() or image.stat().st_size < 512:
                raise RuntimeError(f"Expected a real captured Blender image: {image}")
            if image.is_symlink():
                raise RuntimeError(f"Symlinked image not accepted: {image}")
            with image.open("rb") as fh:
                if fh.read(8) != b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError(f"Not PNG: {image}")
            images.append(str(image.relative_to(ROOT)))
    head, dirty = git_info()
    report = {
        "schema_version": 1,
        "host": host,
        "project_slug": slug,
        "project_commit": head,
        "source_dirty": dirty,
        "renderer_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "shot_ids": shots,
        "images": images,
        "shot_count": len(shots),
        "image_count": len(images),
        "capture_seconds": elapsed,
        "runner_setup_seconds": max(0.0, setup_s),
        "queue_seconds": 0.0,  # Codex populates from actual GitHub run timestamps.
        "transport_seconds": 0.0,  # Codex measures upload/download of the evidence.
        "real_render": True,
        "note": "Same project/frames/quality required; verify render-stills.sh mode is identical.",
    }
    path = output / "performance.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("BENCHMARK_REPORT", path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def choose(local_json: Path | None, cloud_json: Path | None, shots: int) -> dict:
    local = json.loads(local_json.read_text(encoding="utf-8")) if local_json else None
    cloud = json.loads(cloud_json.read_text(encoding="utf-8")) if cloud_json else None
    if local and not cloud:
        return {"chosen_host": "local", "reason": "Only measured local; cloud unmeasured", "verified_comparison": False}
    if cloud and not local:
        return {"chosen_host": "github", "reason": "Local not measured or inaccessible; GitHub fallback", "verified_comparison": False}
    if not local and not cloud:
        raise ValueError("At least one real benchmark report is required")
    for value in (local, cloud):
        if value.get("real_render") is not True or not value.get("capture_seconds", 0) > 0:
            raise ValueError("Invalid or incomplete benchmark report")
    fields = ("project_slug", "project_commit", "renderer_sha256", "shot_ids", "image_count")
    differences = [f for f in fields if local.get(f) != cloud.get(f)]
    if differences or local.get("source_dirty") or cloud.get("source_dirty"):
        return {
            "chosen_host": "github",
            "verified_comparison": False,
            "reason": "Benchmarks are not comparable: " + ", ".join(differences or ["source tree dirty"]) +
                      ". Rerun same scene, shots and source revision; GitHub is safe fallback.",
        }
    if local["host"] != "local" or cloud["host"] != "github":
        raise ValueError("Expected measured host labels local and github")
    n = len(local["shot_ids"])
    multiplier = shots / n
    local_total = local["capture_seconds"] * multiplier + float(local.get("transport_seconds", 0))
    cloud_total = (
        cloud["capture_seconds"] * multiplier
        + float(cloud.get("runner_setup_seconds", 0))
        + float(cloud.get("queue_seconds", 0))
        + float(cloud.get("transport_seconds", 0))
    )
    # Require meaningful cloud advantage; local has less network/polling uncertainty.
    cloud_faster = cloud_total < 0.85 * local_total and local_total - cloud_total > 5
    return {
        "chosen_host": "github" if cloud_faster else "local",
        "verified_comparison": True,
        "project_slug": local["project_slug"],
        "planned_shots": shots,
        "local_estimated_seconds": round(local_total, 1),
        "github_estimated_seconds": round(cloud_total, 1),
        "reason": "GitHub estimated at least 15% and 5 seconds faster" if cloud_faster
                  else "Local remains faster or the GitHub advantage is too small",
        "warning": "Estimates scale sample timing; setup/transport may vary. Rebenchmark after major scene changes.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--slug", required=True)
    c.add_argument("--host", choices=["local", "github"], required=True)
    c.add_argument("--shots", required=True, help="Same comma-separated shot IDs on local and GitHub")
    c.add_argument("--timeout", type=int, default=600)
    c.add_argument("--setup-seconds", type=float, default=0)
    d = sub.add_parser("choose")
    d.add_argument("--local-json", type=Path)
    d.add_argument("--github-json", type=Path)
    d.add_argument("--planned-shots", type=int, default=5)
    args = p.parse_args()
    if args.cmd == "capture":
        if not 10 <= args.timeout <= 3600:
            raise ValueError("Capture timeout must be between 10 and 3600 seconds")
        capture(args.slug, args.host, parse_ids(args.shots), args.timeout, args.setup_seconds)
    else:
        if not 1 <= args.planned_shots <= 1000:
            raise ValueError("planned-shots must be between 1 and 1000")
        print(json.dumps(choose(args.local_json, args.github_json, args.planned_shots),
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
