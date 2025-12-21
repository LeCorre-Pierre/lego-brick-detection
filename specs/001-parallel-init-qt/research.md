# Research & Risks — Initialisation parallèle (Qt)

**Scope**: Startup/initialization architecture for PyQt6 app with parallel threads (set load, camera config, model load).
**Goals**: Keep UI responsive; hit timing targets; handle failures without blocking.

## Performance Targets
- UI window visible & interactive: <2s after launch.
- Set load & brick list render: <1s for typical CSV (<5k rows).
- Camera preview live: <3s after configure; retries non-blocking.
- Model load: background; no UI jank; surface progress.
- Auto-start detection once camera + model ready (and set available when user provides one).

## Known Constraints
- PyQt6 single GUI thread; avoid blocking calls (no wait/sleep on UI thread).
- QThread signal/slot for cross-thread updates; avoid shared mutable state without UI-thread ownership.
- Camera devices may stall/open slowly; OpenCV init can block if not threaded.
- Model load may take up to ~30s; must not freeze UI.

## Risks & Mitigations
- **Camera init hangs**: add timeout/retry, background thread, surface status in UI.
- **Set load on large CSV**: stream parse; early reject huge/empty; keep UI updates minimal.
- **Model load failure**: catch/emit error, keep UI usable; allow retry without restart.
- **Race conditions**: centralize init flags (set/camera/model) and gate auto-start; guard double-starts.
- **UI regressions**: keep all heavy work off UI thread; use QTimer for deferred config load.
- **Performance drift**: add startup timing probes and perf test to track regressions.

## Measurement Plan
- Log timestamps for: app init start, UI show, menu/status bar ready, set load start/finish, camera ready, model ready, detection auto-start.
- pytest-qt integration tests for startup, set load, preview, auto-start; assert timing thresholds.
- Perf script to emit CSV/JSON of timings for CI visibility.

## Dependencies / Inputs
- Spec & plan (this feature).
- Existing BrickDetector, SetCSVLoader, VideoSourceConfigurator, ModelLoader thread stub.
- Sample data: data/import_sample.csv, data/rebrickable_parts_60122-1-volcano-crawler.csv.

## Open Questions
- Should auto-start be user-toggleable (default on)?
- How many preview retry attempts before surfacing blocking dialog?
- Need telemetry output format for CI (CSV vs JSON)?
