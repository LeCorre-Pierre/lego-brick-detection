# 🚀 Démarrage rapide - Outil d'annotation YOLO

Guide de démarrage ultra-rapide pour commencer à annoter vos images LEGO.

## Installation (1 minute)

```bash
# Cloner ou naviguer vers le projet
cd lego-brick-detection

# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# Vérifier les dépendances (déjà installées normalement)
pip install PyQt5 PyYAML Pillow opencv-python numpy
```

## Lancement (30 secondes)

```bash
python src/annotation/run_annotation_tool.py
```

## Créer votre premier dataset (2 minutes)

### 1. Nouveau dataset
- **File → New Dataset...**
- Nom: `my_lego_dataset`
- Chemin: `datasets/my_lego_dataset`
- Classes: garder les 6 classes par défaut (ou personnaliser)
- **Create**

### 2. Importer des images
- **File → Import Images...**
- **Add Folder**: sélectionner votre dossier d'images
- Cocher "Copy images to dataset" (recommandé)
- **Import**

### 3. Annoter
**C'est parti !**

Sélectionner classe:
- Touche **1**: 2x4 Brick
- Touche **2**: 2x2 Brick
- Touche **3**: 1x4 Brick
- etc.

Dessiner bbox:
- **Clic gauche + glisser** sur la brique

Supprimer:
- **Clic droit** sur la bbox

Navigation:
- **→**: Image suivante
- **←**: Image précédente

### 4. Exporter
Une fois annotées (minimum 50-100 images):

1. **Dataset → Split Train/Val...** (split automatique 80/20)
2. **Dataset → Validate Dataset** (vérifier les erreurs)
3. **Dataset → Export YOLO Format...** (export final)

✅ **Votre dataset est prêt pour l'entraînement !**

## Entraîner un modèle (5 minutes)

```python
from ultralytics import YOLO

# Charger modèle pré-entraîné
model = YOLO('yolov8n.pt')

# Entraîner sur votre dataset
model.train(
    data='datasets/my_lego_dataset/data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='lego_detector_v1'
)

# Le modèle entraîné sera dans: runs/detect/lego_detector_v1/weights/best.pt
```

## Tester le modèle

```python
from ultralytics import YOLO

# Charger votre modèle entraîné
model = YOLO('runs/detect/lego_detector_v1/weights/best.pt')

# Prédire
results = model.predict('test_image.jpg', save=True)
# Les résultats sont dans: runs/detect/predict/
```

## Raccourcis essentiels ⚡

| Touche | Action |
|--------|--------|
| `1-6` | Sélectionner classe |
| `←` `→` | Navigation |
| `F` | Ajuster à fenêtre |
| `Delete` | Supprimer bbox |
| `Ctrl S` | Sauvegarder |

## Conseils pour bien démarrer 💡

### 1. Quantité minimale
- **Objectif initial**: 100 images par classe
- **Pour débuter**: 50 images/classe suffisent pour un premier test
- **Qualité > Quantité**: mieux vaut 100 bonnes annotations que 500 mauvaises

### 2. Diversité
Variez dès le début:
- ✅ Angles de vue différents
- ✅ Distances (proche et loin)
- ✅ Éclairages (naturel, artificiel, ombres)
- ✅ Arrière-plans variés
- ✅ Briques seules ET empilées

### 3. Workflow itératif
**Ne pas tout annoter d'un coup !**

1. Annoter 50 images → Entraîner → Tester
2. Identifier erreurs → Ajouter 50 images ciblées → Entraîner
3. Répéter jusqu'à satisfaction

### 4. Qualité des bboxes
- ✅ Bbox **serrée**: englobe la brique sans trop d'espace vide
- ✅ **Complète**: toute la brique visible doit être dans la bbox
- ✅ **Consistante**: toujours annoter de la même manière
- ✅ **Briques partielles**: annoter si >50% visible

## Problèmes fréquents 🔧

### L'application ne démarre pas
```bash
# Vérifier Python
python --version  # Doit être 3.8+

# Réinstaller dépendances
pip install --upgrade PyQt5 PyYAML Pillow opencv-python numpy
```

### Images ne s'affichent pas
- ✅ Vérifier format: JPG ou PNG
- ✅ Vérifier permissions du dossier
- ✅ Essayer de copier images dans le dataset (option Import)

### Erreurs à l'export
- ✅ Vérifier qu'il y a des annotations
- ✅ Faire le split train/val avant export
- ✅ Valider le dataset (Dataset → Validate)

## Prochaines étapes 🎯

1. **Annoter un petit lot** (50-100 images)
2. **Entraîner un premier modèle** (voir code ci-dessus)
3. **Tester sur nouvelles images**
4. **Identifier faiblesses** (quelles briques sont mal détectées ?)
5. **Ajouter images ciblées** pour ces cas difficiles
6. **Répéter** jusqu'à performance satisfaisante

## Ressources 📚

- **Guide complet**: [specs/004-yolo-annotation-tool/USER_GUIDE.md](specs/004-yolo-annotation-tool/USER_GUIDE.md)
- **Documentation API**: [src/annotation/README.md](src/annotation/README.md)
- **YOLO documentation**: https://docs.ultralytics.com/

## Support 💬

Des questions ? Consultez:
1. Le guide utilisateur (lien ci-dessus)
2. Les specs dans `specs/004-yolo-annotation-tool/`
3. Créer une issue GitHub

---

**Bon courage ! 🎨🧱**

*Astuce: Commencez petit, testez souvent, itérez rapidement.*
