#!/bin/bash
# Verification script to confirm all detection code has been removed

echo "=== Detection Code Removal Verification ==="
echo ""

echo "1. Checking for deleted files..."
for file in "src/vision/brick_detector.py" "src/models/detection_params.py" "src/models/detection_result.py" "src/gui/settings_dialog.py" "yolov7_repo"; do
    if [ -e "$file" ]; then
        echo "❌ FAILED: $file still exists"
        exit 1
    else
        echo "✓ $file removed"
    fi
done
echo ""

echo "2. Checking for model files..."
if [ -d "models" ]; then
    pt_files=$(find models -name "*.pt" 2>/dev/null | wc -l)
    if [ "$pt_files" -gt 0 ]; then
        echo "❌ FAILED: Found $pt_files .pt model files in models/"
        exit 1
    else
        echo "✓ No .pt files in models/"
    fi
fi
echo ""

echo "3. Checking Python files for detection imports..."
detection_files=$(find src -name "*.py" -type f -exec grep -l "torch\|yolo\|YOLO\|ultralytics\|BrickDetector\|DetectionParams\|DetectionResult\|QualityConfig" {} \; 2>/dev/null | wc -l)
if [ "$detection_files" -gt 0 ]; then
    echo "❌ FAILED: Found $detection_files files with detection-related code"
    find src -name "*.py" -type f -exec grep -l "torch\|yolo\|YOLO\|ultralytics\|BrickDetector\|DetectionParams\|DetectionResult\|QualityConfig" {} \; 2>/dev/null
    exit 1
else
    echo "✓ No detection imports found in src/"
fi
echo ""

echo "4. Checking requirements.txt..."
if grep -q "torch\|yolo\|ultralytics\|scipy\|tqdm\|seaborn" requirements.txt; then
    echo "❌ FAILED: Detection dependencies still in requirements.txt"
    grep "torch\|yolo\|ultralytics\|scipy\|tqdm\|seaborn" requirements.txt
    exit 1
else
    echo "✓ No detection dependencies in requirements.txt"
fi
echo ""

echo "5. Testing main_window import..."
if python -c "from src.gui.main_window import MainWindow; print('Import successful')" 2>/dev/null; then
    echo "✓ MainWindow imports successfully"
else
    echo "❌ FAILED: MainWindow import failed"
    exit 1
fi
echo ""

echo "6. Checking for test files..."
if [ -d "tests/perf" ]; then
    echo "❌ FAILED: tests/perf/ directory still exists"
    exit 1
else
    echo "✓ tests/perf/ removed"
fi
echo ""

echo "=== ✅ ALL VERIFICATION CHECKS PASSED ==="
echo ""
echo "Summary:"
echo "  - All detection source files removed"
echo "  - All model files removed"
echo "  - All detection imports cleaned up"
echo "  - All ML dependencies removed from requirements.txt"
echo "  - Application still imports successfully"
echo ""
echo "The application is now a simple Lego brick inventory tracker."
