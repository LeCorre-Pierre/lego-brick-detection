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

    def scan_devices(self, max_devices: int = 10) -> List[VideoSource]:
        """Scan for available camera devices."""
        devices = []

        self.logger.info(f"Scanning for camera devices (max {max_devices})...")

        for device_id in range(max_devices):
            device = self._test_device(device_id)
            if device:
                devices.append(device)
                self.logger.info(f"Found device: {device.get_display_name()}")
            else:
                # Stop scanning if we hit consecutive failures
                if device_id > 0 and len(devices) == 0:
                    break

        self.logger.info(f"Scan complete. Found {len(devices)} devices")
        return devices

    def _test_device(self, device_id: int) -> Optional[VideoSource]:
        """Test if a camera device is available and get its properties."""
        try:
            cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)  # Use DirectShow on Windows

            if not cap.isOpened():
                # Try without backend specification
                cap = cv2.VideoCapture(device_id)
                if not cap.isOpened():
                    return None

            # Get device properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # If properties are zero, try to set defaults and read
            if width == 0 or height == 0:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if fps == 0:
                fps = 30  # Default assumption

            cap.release()

            # Create VideoSource object
            device = VideoSource(
                device_id=device_id,
                name=f"Camera {device_id}",
                source_type=VideoSourceType.WEBCAM,
                width=width,
                height=height,
                fps=fps
            )

            return device

        except Exception as e:
            self.logger.debug(f"Error testing device {device_id}: {e}")
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