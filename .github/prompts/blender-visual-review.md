# Codex Cloud (ChatGPT Plus) — visual QA of a real Blender preview

This document is a guide for an **active Codex Cloud task**, NOT an OpenAI API request or an automatic GitHub Actions model call.

1. Read the user's **current new project** only: `projects/<slug>/`, all source references, assets, style instructions and the project-specific Blender renderer.
2. Inspect the real preview output from the matching GitHub Actions run: artifact `blender-preview-<slug>-<run-id>`. Open the real MP4, three frames and `review_strip.png`; verify FPS/resolution/duration from `report.json` and FFprobe where available.
3. Compare rendered imagery with this project's **own** design: objects, rigs, shading, textures, color palette, camera framing, animation, lighting, subtitles and audio. Never reuse the V2 demo or any other project's style.
4. Repair only that project's tracked source under `projects/<slug>/`, making as few changes as necessary. Do not touch other projects, secrets, workflow controls or `main` without reason.
5. Push an authorized project-scoped code change so the project's GitHub workflow renders another real preview. Retrieve the next artifact, inspect it and compare it with the previous preview. Repeat at most **three renders/two correction passes**.
6. Stop early if acceptable, blocked or over usage budget. Include concise notes and verified run/artifact/commit links. Do not claim visual verification of an image you did not open.

**No `OPENAI_API_KEY` needed.** This Codex task runs using the user's eligible ChatGPT Plus access and its rate limits. The GitHub Actions workflow renders only Blender and saves visual evidence; it does not autonomously call Codex. If a task ends before GitHub rendering finishes, the user must resume/start a Codex task or use an independently supported scheduled agent, rather than assuming this file causes background execution.
