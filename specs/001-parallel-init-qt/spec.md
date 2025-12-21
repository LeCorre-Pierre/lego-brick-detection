# Feature Specification: Plan d'architecture — Initialisation parallèle (Qt)

**Feature Branch**: `001-parallel-init-qt`
**Created**: 2025-12-21
**Status**: Closed
**Input**: User description: "Plan d'architecture — Initialisation parallèle (Qt)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Démarrage rapide de l'application (Priority: P1)

En tant qu'utilisateur, je veux que l'application s'affiche immédiatement avec une interface responsive, sans attendre le chargement des composants lourds.

**Why this priority**: C'est l'expérience utilisateur de base - une application qui freeze au démarrage crée une mauvaise première impression et peut faire penser que l'application est plantée.

**Independent Test**: Peut être testé indépendamment en lançant l'application et vérifiant que la fenêtre apparaît en moins de 2 secondes, avec tous les contrôles cliquables.

**Acceptance Scenarios**:

1. **Given** l'application est lancée, **When** l'utilisateur attend, **Then** la fenêtre principale apparaît en moins de 2 secondes avec tous les menus et boutons accessibles
2. **Given** la fenêtre est affichée, **When** l'utilisateur clique sur les menus, **Then** ils répondent immédiatement sans freeze

---

### User Story 2 - Chargement rapide du set Lego (Priority: P2)

En tant qu'utilisateur, je veux voir mon set Lego chargé et affiché immédiatement après sélection du fichier, sans attendre les autres composants.

**Why this priority**: Permet à l'utilisateur de voir rapidement les briques à chercher, améliorant l'expérience utilisateur pendant l'attente des autres composants.

**Independent Test**: Peut être testé en chargeant un fichier CSV et vérifiant que la liste des briques apparaît en moins de 1 seconde.

**Acceptance Scenarios**:

1. **Given** un fichier CSV de set Lego valide, **When** l'utilisateur le charge, **Then** la liste des briques apparaît en moins de 1 seconde
2. **Given** le set est chargé, **When** l'utilisateur fait défiler la liste, **Then** elle est fluide et responsive

---

### User Story 3 - Preview caméra automatique (Priority: P2)

En tant qu'utilisateur, je veux voir le preview de ma caméra dès que possible, même si la détection n'est pas encore active.

**Why this priority**: Permet à l'utilisateur de vérifier que la caméra fonctionne et de positionner les briques pendant le chargement du modèle IA.

**Independent Test**: Peut être testé en configurant une caméra et vérifiant que le flux vidéo apparaît en moins de 3 secondes.

**Acceptance Scenarios**:

1. **Given** une caméra est configurée, **When** l'utilisateur attend, **Then** le preview vidéo apparaît en moins de 3 secondes
2. **Given** le preview fonctionne, **When** l'utilisateur bouge la caméra, **Then** le flux vidéo se met à jour en temps réel

---

### User Story 4 - Détection automatique (Priority: P3)

En tant qu'utilisateur, je veux que la détection démarre automatiquement dès que tous les composants sont prêts, sans action manuelle.

**Why this priority**: Simplifie l'utilisation - l'utilisateur n'a pas besoin de se souvenir de cliquer sur "Start Detection".

**Independent Test**: Peut être testé en chargeant set + caméra + modèle et vérifiant que la détection démarre automatiquement.

**Acceptance Scenarios**:

1. **Given** set chargé, caméra configurée et modèle prêt, **When** tous les composants sont initialisés, **Then** la détection démarre automatiquement
2. **Given** la détection fonctionne, **When** l'utilisateur voit des briques détectées, **Then** il peut cliquer dessus pour les marquer

---

### Edge Cases

- Que se passe-t-il si le fichier CSV du set est corrompu ou trop volumineux ?
- Comment le système gère-t-il une caméra déconnectée pendant l'initialisation ?
- Que faire si le chargement du modèle IA échoue (mémoire insuffisante, fichier manquant) ?
- Comment gérer plusieurs caméras disponibles ?
- Que se passe-t-il si l'utilisateur ferme l'application pendant l'initialisation ?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: L'application DOIT afficher la fenêtre principale en moins de 2 secondes après le lancement
- **FR-002**: L'application DOIT permettre l'interaction complète avec l'interface (menus, boutons) immédiatement après affichage
- **FR-003**: Le système DOIT charger les fichiers CSV de set Lego en moins de 1 seconde
- **FR-004**: Le système DOIT afficher la liste des briques immédiatement après chargement du set
- **FR-005**: Le système DOIT établir la connexion caméra et afficher le preview en moins de 3 secondes
- **FR-006**: Le système DOIT charger le modèle IA en arrière-plan sans bloquer l'interface
- **FR-007**: Le système DOIT activer automatiquement la détection quand caméra ET modèle sont prêts
- **FR-008**: Le système DOIT utiliser des threads séparés pour chaque tâche lourde (chargement set, caméra, modèle)
- **FR-009**: Le système DOIT communiquer entre threads uniquement via les signaux Qt
- **FR-010**: Le système NE DOIT PAS utiliser wait(), sleep() ou opérations bloquantes dans le thread UI

### Key Entities *(include if feature involves data)*

- **ThreadConfig**: Thread responsable du chargement et parsing des fichiers de configuration set
- **ThreadCamera**: Thread responsable de l'ouverture, configuration et streaming de la caméra
- **ThreadModel**: Thread responsable du chargement et préparation du modèle IA
- **UIState**: État partagé entre threads (flags config_ok, camera_ok, model_ok)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: L'application s'affiche en moins de 2 secondes après lancement
- **SC-002**: L'interface reste responsive (pas de freeze) pendant toute la phase d'initialisation
- **SC-003**: Les sets Lego se chargent et s'affichent en moins de 1 seconde
- **SC-004**: Le preview caméra apparaît en moins de 3 secondes après configuration
- **SC-005**: Le modèle IA se charge en arrière-plan sans impact sur l'interface
- **SC-006**: La détection démarre automatiquement quand tous les composants sont prêts
- **SC-007**: Aucun blocage du thread UI pendant l'initialisation (mesuré par responsiveness des contrôles)
- **SC-008**: Utilisation mémoire stable pendant l'initialisation parallèle

## Assumptions

- Le système dispose de ressources suffisantes (CPU, mémoire) pour exécuter les threads en parallèle
- Les fichiers CSV de set Lego sont dans un format standard et valide
- Au moins une caméra est disponible sur le système
- Le modèle IA peut être chargé dans un délai raisonnable (max 30 secondes)

## Dependencies

- PyQt6 pour la gestion des threads et signaux
- OpenCV pour l'accès caméra
- Système de fichiers pour le chargement des sets
- Bibliothèque IA (TensorFlow/PyTorch/ONNX) pour le chargement du modèle

## Implementation Notes

### Architecture Technique

**Thread UI (Principal)**:
- Affiche l'interface immédiatement
- Lance les threads workers
- Réagit aux signaux des threads
- Met à jour l'affichage en temps réel

**Thread Configuration**:
- Charge et parse les fichiers CSV
- Émet signal `config_ready(data)`
- Très rapide (< 1s)

**Thread Caméra**:
- Ouvre et configure le périphérique caméra
- Démarre le streaming vidéo
- Émet signaux `camera_ready()` et `frame_available(frame)`
- Moyen (2-3s)

**Thread Modèle IA**:
- Charge le modèle depuis le disque
- Prépare le pipeline d'inférence
- Émet signal `model_ready(model)`
- Lent (jusqu'à 30s)

### Synchronisation

```python
# État partagé dans le thread UI
config_ok = False
camera_ok = False
model_ok = False

# Callbacks déclenchés par signaux
def on_config_ready(): config_ok = True
def on_camera_ready(): camera_ok = True
def on_model_ready(): model_ok = True

# Condition de démarrage automatique
if camera_ok and model_ok:
    start_detection()
```

### Gestion d'Erreurs

- Chaque thread gère ses propres erreurs et émet des signaux d'erreur
- Le thread UI affiche les erreurs à l'utilisateur sans crasher
- L'application reste fonctionnelle même si certains composants échouent

## Testing Strategy

### Unit Tests
- Test de chaque thread worker indépendamment
- Test des signaux Qt émis
- Test de gestion d'erreurs

### Integration Tests
- Test de l'initialisation complète
- Test des scénarios de synchronisation
- Test de performance (temps de démarrage)

### User Acceptance Tests
- Test de l'expérience utilisateur complète
- Test sur différentes configurations matérielles
- Test de robustesse (caméra déconnectée, fichiers corrompus)
