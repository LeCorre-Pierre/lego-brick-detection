"""
Custom widget for individual brick entries in the brick list.
Displays brick information including preview image, ID, name, and quantity.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QMouseEvent
from typing import Optional
from ..models.brick import Brick
from ..utils.image_cache import ImageCache


class BrickListItem(QWidget):
    """Custom widget for displaying individual brick information in a list."""
    
    # Signals
    counter_incremented = pyqtSignal()  # Emitted when left-clicked
    counter_decremented = pyqtSignal()  # Emitted when right-clicked
    manually_marked_changed = pyqtSignal(bool)  # Will be used in Phase 5
    
    def __init__(self, brick: Brick, image_cache: ImageCache, parent=None):
        """
        Initialize brick list item.
        
        Args:
            brick: The Brick object to display
            image_cache: ImageCache instance for loading preview images
            parent: Parent widget
        """
        super().__init__(parent)
        self.brick = brick
        self.image_cache = image_cache
        self._is_complete = False
        
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        """Setup the user interface layout."""
        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Preview image (48x48)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(48, 48)
        self.preview_label.setScaledContents(False)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # Brick information (ID, name, quantity) in vertical layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Brick ID - prominent display
        self.id_label = QLabel()
        id_font = QFont()
        id_font.setBold(True)
        id_font.setPointSize(10)
        self.id_label.setFont(id_font)
        info_layout.addWidget(self.id_label)
        
        # Brick name with color
        self.name_label = QLabel()
        name_font = QFont()
        name_font.setPointSize(8)
        self.name_label.setFont(name_font)
        self.name_label.setWordWrap(False)
        # Truncate long names with ellipsis
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        info_layout.addWidget(self.name_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, stretch=1)
        
        # Counter display label (format: "X/Y")
        self.counter_label = QLabel()
        counter_font = QFont()
        counter_font.setPointSize(10)
        counter_font.setBold(True)
        self.counter_label.setFont(counter_font)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.counter_label.setMinimumWidth(50)
        layout.addWidget(self.counter_label)
        
        # Required quantity label (right side)
        self.quantity_label = QLabel()
        quantity_font = QFont()
        quantity_font.setPointSize(9)
        self.quantity_label.setFont(quantity_font)
        self.quantity_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.quantity_label.setMinimumWidth(60)
        layout.addWidget(self.quantity_label)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
    
    def _update_display(self):
        """Update all display elements with current brick data."""
        # Load and display preview image
        pixmap = self.image_cache.get_image(self.brick.part_number)
        self.preview_label.setPixmap(pixmap)
        
        # Display brick ID
        self.id_label.setText(f"#{self.brick.part_number}")
        
        # Display brick name (with ellipsis for long names)
        name_text = self.brick.name
        if len(name_text) > 30:
            name_text = name_text[:27] + "..."
        self.name_label.setText(name_text)
        
        # Display required quantity
        self.quantity_label.setText(f"Need: {self.brick.quantity}")
        
        # Display counter
        self.update_counter_display(self.brick.found_quantity, self.brick.quantity)
    
    def set_brick(self, brick: Brick) -> None:
        """
        Set the brick data for this list item.
        
        Args:
            brick: The Brick object to display
        """
        self.brick = brick
        self._update_display()
    
    def get_brick_id(self) -> str:
        """
        Get the part number of this brick.
        
        Returns:
            The brick's part number
        """
        return self.brick.part_number
    
    def update_counter_display(self, found_count: int, required_count: int) -> None:
        """Update the counter display and apply completion highlighting."""
        self.counter_label.setText(f"{found_count}/{required_count}")
        
        # Apply or remove completion highlight
        if found_count >= required_count:
            if not self._is_complete:
                self._apply_completion_highlight()
                self._is_complete = True
        else:
            if self._is_complete:
                self._remove_completion_highlight()
                self._is_complete = False
    
    def _apply_completion_highlight(self) -> None:
        """Apply green highlight to indicate brick collection is complete."""
        self.setStyleSheet("""
            QWidget {
                background-color: #c8e6c9;
            }
        """)
    
    def _remove_completion_highlight(self) -> None:
        """Remove completion highlight."""
        self.setStyleSheet("")
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse clicks for counter increment/decrement."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.counter_incremented.emit()
        elif event.button() == Qt.MouseButton.RightButton:
            self.counter_decremented.emit()
        
        super().mousePressEvent(event)
    
    def sizeHint(self) -> QSize:
        """Return the recommended size for this widget."""
        return QSize(400, 60)
