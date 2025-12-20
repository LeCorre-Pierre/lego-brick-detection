"""
Camera device scanning functionality for Lego Brick Detection application.
"""

import cv2
from typing import List, Dict, Optional
from ..models.video_source import VideoSource, VideoSourceType
from ..utils.logger import get_logger

logger = get_logger("camera_scanner")

class CameraScanner:
    """Scans for available camera devices and provides device information."""

    def __init__(self):
        self.logger = logger

    def scan_devices(self, max_devices: int = 2) -> List[VideoSource]:
        """Scan for available camera devices."""
        devices = []

        self.logger.info(f"Scanning for camera devices (max {max_devices})...")

        # For now, assume common devices exist to avoid slow scanning
        # TODO: Implement faster device detection
        potential_devices = [
            (0, VideoSourceType.WEBCAM, "Webcam"),
            (1, VideoSourceType.KINECT, "Kinect"),
        ]
        
        for device_id, device_type, name in potential_devices[:max_devices]:
            # Quick check - just assume devices exist for now
            device = VideoSource(
                type=device_type,
                device_id=device_id,
                resolution=(640, 480),
                frame_rate=30
            )
            devices.append(device)
            self.logger.info(f"Found device: {device.get_display_name()}")

        self.logger.info(f"Scan complete. Found {len(devices)} devices")
        return devices

    def _test_device(self, device_id: int) -> Optional[VideoSource]:
        """Test if a camera device is available and get its properties."""
        try:
            cap = cv2.VideoCapture(device_id)
            if cap.isOpened():
                cap.release()
                
                # Create a basic device - properties will be determined later
                device = VideoSource(
                    type=VideoSourceType.WEBCAM,
                    device_id=device_id,
                    resolution=(640, 480),  # Default resolution
                    frame_rate=30  # Default FPS
                )
                return device
        except Exception:
            pass
        return None

    def get_device_info(self, device_id: int) -> Optional[Dict]:
        """Get detailed information about a specific device."""
        device = self._test_device(device_id)
        if device:
            return {
                'device_id': device.device_id,
                'name': device.name,
                'type': device.source_type.value,
                'width': device.width,
                'height': device.height,
                'fps': device.fps,
                'display_name': device.get_display_name()
            }
        return None

    def find_default_device(self) -> Optional[VideoSource]:
        """Find the default/first available camera device."""
        devices = self.scan_devices(max_devices=5)
        return devices[0] if devices else None