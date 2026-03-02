# LEGO Detection Model Zoo (Accessible)

Last verified: 2026-03-02

## Fast shortlist (best first)

1. B200 custom YOLO model (local): `models/b200-epoch50.pt` in this repo.
2. Roboflow Hex LEGO (hosted API): https://universe.roboflow.com/craftyblocks/hex-lego-yk2pe
3. Roboflow Lego Detection (22 classes): https://universe.roboflow.com/sigisudoku/lego-detection-zng1h/model/5
4. Hugging Face YOLOv7 LEGO (single-class): https://huggingface.co/mw00/yolov7-lego

## Accessible models found

1. https://universe.roboflow.com/craftyblocks/hex-lego-yk2pe
2. https://universe.roboflow.com/26l-dg2qg/lego-jn4ap-tovjk/model/5
3. https://universe.roboflow.com/legotest/my-first-project-5txys/model/24
4. https://universe.roboflow.com/sigisudoku/lego-detection-zng1h/model/5
5. https://universe.roboflow.com/lego-gzcvi/lego-364li-w5rf5/model/1
6. https://universe.roboflow.com/legotest-lmpuo/lego-jn4ap-mbzgb/model/1
7. https://universe.roboflow.com/mycameraapp/lego-defect-detection-lfsf2/model/14
8. https://universe.roboflow.com/mycameraapp/lego-assembly-manual-detection-okuq0/model/1
9. https://universe.roboflow.com/imadham2/detection-22-ie7fn/model/1
10. https://universe.roboflow.com/bmodra/lego-head-detector/model/1
11. https://huggingface.co/mw00/yolov7-lego
12. local model in repo: `models/b200-epoch50.pt`

## Notes

- Roboflow models are immediately callable through hosted inference (API key required).
- The Hugging Face model provides downloadable `.pt` weights (single-class LEGO detector).
- For this project architecture, YOLOv8 `.pt` local model + optional Roboflow fallback is the most stable path.
