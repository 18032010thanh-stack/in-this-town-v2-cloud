# Codex operating instructions — Blender cloud projects

For any new Blender project, animation, video, ZIP/asset pack, preview render or GitHub Actions render request, automatically open and follow **`.agents/skills/blender-github-autopilot/SKILL.md`**. Do not wait for the user to repeat “use GitHub”, “run the workflow”, “check logs” or “download artifacts”; these are parts of the assigned work.

- For every NEW project, examine all supplied assets/scripts/docs; use its own style, rigs, materials, characters, narration and render engine. Never borrow assets or visual style from previous projects.
- Keep new projects in **`projects/<project-slug>/`** and each workflow in **`.github/workflows/render-<project-slug>.yml`**. Do not overwrite the existing In This Town V2 project or its workflow, or any V1 project.
- If permitted to write GitHub files but not to invoke workflow_dispatch, configure a project-scoped **push** workflow, commit the changes, identify the resulting Actions run, follow logs, fix errors if possible, and retrieve/verify the real MP4 artifact.
- Start with a short **production-grade actual Blender test**, then render a full film only when requested. Never call a mock/2D rendering a genuine Blender render.
- This repo is **public**. Do not upload new confidential/unlicensed third-party source assets here, or create public releases, without authorization for the specific new project. If rights/access make that impossible, ask only for the one essential choice.
- Use real job/commit/artifact IDs. Respect GitHub quotas and reject duplicate ongoing runs. Do not claim an output exists without verifying it.
- GitHub CI can continue after the chat finishes; the chat assistant itself cannot continue asynchronously without a scheduled automation.

The existing root V2 production test is historical project-specific material, **not the default source of style or assets** for new tasks.

## Codex Cloud with ChatGPT Plus — no OpenAI API key

For new projects, use the [blender-github-autopilot](.agents/skills/blender-github-autopilot/SKILL.md) skill. The project-scoped GitHub Actions workflow `.github/workflows/blender-visual-autopilot.yml` renders **real Blender previews only**, saves a 3-frame QA strip, and publishes a video artifact. It does **not** run Codex inside CI.

While carrying out an active **Codex Cloud** task, Codex must read the actual GitHub run and artifact, examine the images against that project's own style and assets, fix relevant source code, push a project-specific change and rerender (maximum three previews/two correction rounds). Do not copy assets, material or style from the existing V2 project. Don't claim the AI will run unattended after the Codex task has finished.

**No `OPENAI_API_KEY` secret is required or requested.** The user's ChatGPT Plus includes eligible Codex use subject to plan limits; GitHub Actions rendering still has separate resource limits. A specific new project must provide its own audited renderer at `projects/<slug>/render-preview.sh` and a push-triggered driver, so the workflow is not started for historical V2 content by mistake.

## Hybrid renderer selection (the user's preferred default)

The user has a **weak local PC with Blender** and uses **ChatGPT Plus Codex without OpenAI API**. When a NEW project arrives, Codex should first build/inspect the project using its own asset/style/rig/renderer. For **3 stills per shot** (start/middle/end), benchmark local Blender + MCP/viewport **if a real local bridge exists** against GitHub Actions with the same settings, and choose the faster overall path (queue, install, transport, capture). Use `.github/scripts/blender_hybrid_probe.py` and `.github/workflows/blender-hybrid-benchmark.yml`. If local isn't connected or can't capture reliably, **use GitHub**, label local performance unmeasured rather than slower. Keep video final rendering on GitHub. No `OPENAI_API_KEY` secret, in-workflow Codex/AI API, or promise of automatic Codex wake-ups after its task finishes. Prefer local for fast layout checks when viable; use cloud for expensive realistic stills. Recheck benchmarking when scene/quality changes. Respect project-specific style, source integrity, license and bounded rerenders.
