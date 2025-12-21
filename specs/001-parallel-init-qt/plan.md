# Implementation Plan: Plan d'architecture — Initialisation parallèle (Qt)

**Branch**: `001-parallel-init-qt` | **Date**: 2025-12-21 | **Spec**: [specs/001-parallel-init-qt/spec.md](specs/001-parallel-init-qt/spec.md)
**Status**: Closed
**Input**: Feature specification from `/specs/001-parallel-init-qt/spec.md`

## Summary

Architecture d'initialisation parallèle pour PyQt6 : l'UI se montre instantanément, chaque tâche lourde (chargement set, configuration caméra, chargement modèle IA) s'exécute dans son thread dédié via signaux Qt, avec démarrage automatique de la détection dès que caméra et modèle sont prêts, sans bloquer le thread UI.

Closure: Documentation complete (research, data-model, quickstart). Implementation partially applied (logging fixes and set progress refresh) and feature marked closed per request.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PyQt6 (UI + QThread + signaux), OpenCV (capture vidéo), NumPy; modèle IA actuel encapsulé dans `BrickDetector`  
**Storage**: Fichiers locaux (CSV sets) uniquement  
**Testing**: pytest (à renforcer pour threads/signaux)  
**Target Platform**: Desktop Windows/Linux (Kinect v1 ou webcam)  
**Project Type**: Single desktop app (PyQt6)  
**Performance Goals**: UI affichée < 2s; chargement set < 1s; preview caméra < 3s; détection auto dès `camera_ok && model_ok`; UI jamais bloquée  
**Constraints**: Pas de blocage dans le thread UI (pas de wait/sleep lourds); communication uniquement par signaux Qt; mémoire stable pendant init; gestion erreurs non bloquante  
**Scale/Scope**: Application desktop unique; un flux vidéo; set Lego typique (quelques centaines d'entrées max)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Accurate spotting of Lego bricks in piles? **Yes** — architecture maintient BrickDetector et pipeline temps réel.
- Detection based on predefined set pieces? **Yes** — set chargé en thread config, appliqué au détecteur.
- Prevent re-detection after pickup? **Yes** — logique existante de stabilité/état conservée; plan ne la casse pas.
- Real-time video input (Kinect/webcam)? **Yes** — ThreadCaméra dédié, preview rapide, aucun blocage UI.
- Various lighting/angles accounted for? **Yes** — paramètres de détection existants, architecture non bloquante pour ajustements rapides.

## Project Structure

### Documentation (this feature)

```text
specs/001-parallel-init-qt/
├── plan.md              # Plan (/speckit.plan output)
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── gui/               # PyQt6 UI, MainWindow, dialogs, video display
├── vision/            # BrickDetector, camera scanner, color/contour
├── loaders/           # Set loading (CSV)
├── models/            # Domain models (lego_set, video_source, params)
├── utils/             # Logger, config manager, progress tracker
└── detect.py, main.py # Entry points / CLI

tests/
└── (to be expanded for threading/signals and integration)
```

**Structure Decision**: Single desktop PyQt6 project; threads gérés dans `src/gui/main_window.py` et workers dans `src/loaders` / `src/vision`; pas de sous-projets supplémentaires.

## Complexity Tracking

No constitution violations; tracking table not required.
