# In This Town V2 — Real Blender Cloud Pilot

**ONLY user-supplied V2 source.** No V1 sources, old films, prior 2D scripts, Robot Seed or replacement visual assets.

This repository stores the user's exact V2-only production package as `source/In_This_Town_V2_OneClick_Cloud_11s.zip`, checked with Git blob SHA `55aef40ad508ddf8c3b04abeaf254024c1e18c5c` and SHA-256 `ac74551c8fc56692f0515cb4f564ba69bb127844ed35a9de3ed44be24fa4a2f7`.

The runner extracts this package and verifies the hashes of all 64 original V2 files. Narrow runtime-only patches for Blender compatibility and silent-shot timing are applied in a separate `_runtime_v2` folder. Original V2 source stays unchanged.

## Real production test (not full episode)

- V2 Episode 03 first 13 original shots; ~11.87 seconds at 24 FPS.
- Original V2 Blender scene engine, 8 original sets, 44 camera rigs, 8 source textures and original face design. 1080×1920 Cycles CPU.
- Original V2 Vietnamese Edge TTS voice and **word-level subtitles**, without additional music.
- Preflight: 64-file audit, tests, 3D stills, voice, then one full-resolution Blender frame.
- Three parallel jobs (95 frames each) only after preflight passes.
- Assemble: validate all 285 real JPEG frames; export `FINAL.mp4` and `test_v2_vietsub.srt`.

Run workflow: [V2 ONLY — production Blender test 11.87s](../../actions/workflows/v2-real-production-test.yml).

Final artifact: `V2-ep03-real-3D-test-11s` with 7-day retention.

**Cost/privacy note:** This repository is Public by the owner's choice. Cloud runs consume GitHub Actions minutes/storage under account limits; do not start duplicate runs. Presence of material in a supplied archive is not an independent verification of redistribution rights.
