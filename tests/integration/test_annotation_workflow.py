"""
Integration tests for the annotation system.
"""

import pytest
from pathlib import Path
import shutil
import tempfile
from PIL import Image
import numpy as np

from src.annotation.models import (
    Annotation, AnnotatedImage, BrickClass, Dataset, AnnotationProject
)
from src.annotation.annotation_manager import AnnotationManager
from src.annotation.dataset_builder import DatasetBuilder
from src.annotation.yolo_format import YoloFormatter


def create_test_image(path: Path, width: int = 640, height: int = 480):
    """Create a simple test image."""
    # Create a random RGB image
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(path)


@pytest.fixture
def temp_dataset_dir():
    """Create a temporary directory for test datasets."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_classes():
    """Sample brick classes."""
    return [
        BrickClass(id=0, name="2x4_brick", display_name="2x4 Brick", color=(255, 0, 0)),
        BrickClass(id=1, name="2x2_brick", display_name="2x2 Brick", color=(0, 255, 0)),
        BrickClass(id=2, name="1x4_brick", display_name="1x4 Brick", color=(0, 0, 255)),
    ]


def test_full_workflow_dataset_creation_and_export(temp_dataset_dir, sample_classes):
    """Test complete workflow from dataset creation to YOLO export."""
    
    # 1. Create a dataset
    dataset = DatasetBuilder.create_dataset(
        name="test_dataset",
        root_path=temp_dataset_dir / "test_dataset",
        classes=sample_classes
    )
    
    assert dataset.name == "test_dataset"
    assert len(dataset.classes) == 3
    assert dataset.root_path.exists()
    assert (dataset.root_path / "images").exists()
    
    # 2. Create some test images (just copy from existing if available)
    # For now, we'll simulate by creating placeholder image paths
    test_images = []
    for i in range(5):
        img_path = dataset.root_path / "images" / f"test_img_{i}.jpg"
        # Create test image
        create_test_image(img_path)
        test_images.append(img_path)
    
    # 3. Add images to dataset
    for img_path in test_images:
        dataset.add_image(img_path)
    
    assert dataset.num_images == 5
    
    # 4. Add annotations to images
    for img in dataset.images:
        # Add some annotations
        ann1 = Annotation.from_pixel_coords(
            class_id=0,
            class_name="2x4_brick",
            x=50, y=50, w=100, h=100,
            img_width=640, img_height=480
        )
        ann2 = Annotation.from_pixel_coords(
            class_id=1,
            class_name="2x2_brick",
            x=200, y=150, w=80, h=80,
            img_width=640, img_height=480
        )
        img.add_annotation(ann1)
        img.add_annotation(ann2)
    
    assert dataset.num_annotations == 10  # 2 annotations per 5 images
    
    # 5. Split train/val
    DatasetBuilder.split_train_val(dataset, ratio=0.8, shuffle=True)
    
    assert dataset.num_train == 4
    assert dataset.num_val == 1
    
    # 6. Export to YOLO format
    success = DatasetBuilder.export_dataset(dataset)
    
    assert success
    assert (dataset.root_path / "labels").exists()
    assert (dataset.root_path / "labels" / "train").exists()
    assert (dataset.root_path / "labels" / "val").exists()
    assert (dataset.root_path / "data.yaml").exists()
    
    # 7. Validate YOLO files
    # Check that label files were created
    train_label_dir = dataset.root_path / "labels" / "train"
    val_label_dir = dataset.root_path / "labels" / "val"
    
    train_labels = list(train_label_dir.glob("*.txt"))
    val_labels = list(val_label_dir.glob("*.txt"))
    
    assert len(train_labels) == 4
    assert len(val_labels) == 1
    
    # 8. Check data.yaml content
    import yaml
    with open(dataset.root_path / "data.yaml", "r") as f:
        data_yaml = yaml.safe_load(f)
    
    assert data_yaml['nc'] == 3
    assert len(data_yaml['names']) == 3
    assert data_yaml['names'][0] == "2x4_brick"  # Uses 'name' field, not 'display_name'


def test_annotation_manager_crud_operations(temp_dataset_dir, sample_classes):
    """Test AnnotationManager CRUD operations."""
    
    # Create dataset
    dataset = DatasetBuilder.create_dataset(
        name="test_manager_dataset",
        root_path=temp_dataset_dir / "manager_test",
        classes=sample_classes
    )
    
    # Add test images first
    for i in range(3):
        img_path = dataset.root_path / "images" / f"test_{i}.jpg"
        create_test_image(img_path)
        dataset.add_image(img_path)
    
    # Create manager after adding images
    manager = AnnotationManager()
    manager.create_new_project(dataset)
    
    # Should start at first image
    assert manager.current_image_index == 0
    assert manager.current_image is not None
    
    # Create annotation
    ann = manager.create_annotation(
        image_path=manager.current_image.image_path,
        class_id=0,
        class_name="2x4_brick",
        x=100, y=100, w=200, h=150,
        img_width=640, img_height=480
    )
    
    assert ann is not None
    assert manager.current_image.annotation_count == 1
    
    # Update annotation (change bbox)
    success = manager.update_annotation(
        ann.id,
        x=150, y=150, w=250, h=200,
        img_width=640, img_height=480
    )
    assert success
    # Verify bbox changed
    assert ann.x_center != 0.5
    
    # Navigate
    manager.next_image()
    assert manager.current_image_index == 1
    
    manager.previous_image()
    assert manager.current_image_index == 0
    
    # Delete annotation
    success = manager.delete_annotation(ann.id)
    assert success
    assert manager.current_image.annotation_count == 0
    
    # Save and load project
    project_path = dataset.root_path / "project.json"
    success = manager.save_project(project_path)
    assert success
    assert project_path.exists()
    
    # Load project
    new_manager = AnnotationManager()
    new_manager.load_project(project_path)
    
    assert new_manager.dataset.name == "test_manager_dataset"
    assert new_manager.dataset.num_images == 3


def test_yolo_format_conversion():
    """Test YOLO format conversions."""
    
    # Test pixel to normalized
    x_norm, y_norm, w_norm, h_norm = YoloFormatter.pixel_to_normalized(
        x=100, y=100, w=200, h=150,
        img_width=640, img_height=480
    )
    
    assert 0 <= x_norm <= 1
    assert 0 <= y_norm <= 1
    assert 0 <= w_norm <= 1
    assert 0 <= h_norm <= 1
    
    # Test normalized to pixel
    x_pix, y_pix, w_pix, h_pix = YoloFormatter.normalized_to_pixel(
        x_norm, y_norm, w_norm, h_norm,
        img_width=640, img_height=480
    )
    
    # Should be close to original (within rounding error)
    assert abs(x_pix - 100) < 2
    assert abs(y_pix - 100) < 2
    assert abs(w_pix - 200) < 2
    assert abs(h_pix - 150) < 2


def test_dataset_statistics(temp_dataset_dir, sample_classes):
    """Test dataset statistics calculation."""
    
    dataset = DatasetBuilder.create_dataset(
        name="stats_test",
        root_path=temp_dataset_dir / "stats_test",
        classes=sample_classes
    )
    
    # Add images with varying annotation counts
    for i in range(10):
        img_path = dataset.root_path / "images" / f"img_{i}.jpg"
        create_test_image(img_path)
        dataset.add_image(img_path)
        
        # Add random number of annotations per class
        for class_id in range(3):
            num_anns = i % 3  # 0, 1, or 2 annotations
            for _ in range(num_anns):
                ann = Annotation.from_pixel_coords(
                    class_id=class_id,
                    class_name=f"brick_{class_id}",
                    x=50, y=50, w=100, h=100,
                    img_width=640, img_height=480
                )
                dataset.images[i].add_annotation(ann)
    
    stats = dataset.get_statistics()
    
    assert stats['total_images'] == 10
    assert stats['total_annotations'] > 0
    assert 'class_distribution' in stats
    assert len(stats['class_distribution']) <= 3


def test_validation_catches_errors(temp_dataset_dir, sample_classes):
    """Test that validation catches common errors."""
    
    dataset = DatasetBuilder.create_dataset(
        name="validation_test",
        root_path=temp_dataset_dir / "validation_test",
        classes=sample_classes
    )
    
    # Add an image
    img_path = dataset.root_path / "images" / "test.jpg"
    create_test_image(img_path)
    dataset.add_image(img_path)
    
    # Add annotation with out-of-bounds coordinates
    img = dataset.images[0]
    ann_invalid = Annotation(
        id="invalid",
        class_id=0,
        class_name="2x4_brick",
        x_center=1.5,  # Invalid: > 1.0
        y_center=0.5,
        width=0.2,
        height=0.2
    )
    img.annotations.append(ann_invalid)
    
    # Validate
    errors = DatasetBuilder.validate_dataset(dataset)
    
    # Debug: print errors
    print(f"Validation errors: {errors}")
    
    # Should catch the out-of-bounds error
    assert len(errors) > 0
    assert any("Invalid x_center" in err or "out of bounds" in err.lower() for err in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
