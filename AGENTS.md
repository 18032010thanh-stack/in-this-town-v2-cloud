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

## Autonomous render → visual inspection → fix loop

For any NEW Blender project whose preview render needs iterative improvements, invoke the reusable workflow at `.github/workflows/blender-visual-autopilot.yml` as specified in the `blender-github-autopilot` skill. Have the NEW project provide its own `projects/<slug>/render-preview.sh`, `ci-setup.sh` if needed, and a project-scoped push trigger. Codex will inspect a contact sheet of three actual Blender frames, edit only that project, rerender (up to 3 render rounds), and open a review PR for changes when permitted. Do not reuse style or assets from this repository's V2 production test. Require `OPENAI_API_KEY` as a GitHub Actions secret; never put the API key in source code or conversation. The workflow does not self-start until a new project-specific trigger is committed or a manual run is requested.
