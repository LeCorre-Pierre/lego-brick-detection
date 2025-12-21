# Quickstart — Initialisation parallèle (Qt)

## Scenario 1: Fast startup baseline
1. Launch `python src/main.py`.
2. Expect window visible and menus clickable <2s; status bar shows "Ready" then init progress.
3. Verify no UI freeze while model/set/camera threads start.

## Scenario 2: Load set quickly
1. In app, File → Load Set… choose `data/import_sample.csv`.
2. Expect brick list populated <1s; scrolling is responsive.
3. Status bar shows load message; no modal blocks.

## Scenario 3: Camera preview without model
1. Camera → Configure… select device; accept.
2. Expect preview within <3s, even if model still loading.
3. Status bar/overlay shows preview active; detection disabled until model ready.

## Scenario 4: Auto-start detection when ready
1. Launch with set file argument and camera index (if supported) or load set + configure camera manually.
2. Wait for model load completion.
3. Expect detection to auto-start when set + camera + model ready; UI indicates detecting.

## Scenario 5: Error handling (camera unavailable)
1. Start with unplugged camera; attempt configure.
2. Expect non-blocking error message and ability to retry; UI stays responsive.

## Scenario 6: Large/invalid set file
1. Attempt to load oversized or malformed CSV.
2. Expect early warning/error; no freeze; previous state preserved.

## Validation Notes
- Record timestamps from logs for startup, set load, preview, model load, auto-start.
- Use pytest-qt integration tests to automate Scenarios 1–4.
- Manual check acceptable for Scenarios 5–6 initially; codify later if feasible.
