"""
Video stream testing functionality for Lego Brick Detection application.
"""

import cv2
import time
from typing import Dict, Optional, Tuple
from ..models.video_source import VideoSource
from ..vision.video_utils import VideoCaptureManager
from ..utils.logger import get_logger

logger = get_logger("video_tester")

class VideoTester:
    """Tests video streams and provides quality metrics."""

    def __init__(self):
        self.logger = logger

    def test_stream(self, video_source: VideoSource, test_duration: float = 5.0) -> Dict:
        """Test a video stream and return quality metrics."""
        results = {
            'success': False,
            'error': None,
            'metrics': {},
            'frames_captured': 0,
            'avg_fps': 0.0,
            'resolution': (0, 0),
            'brightness': 0.0,
            'stability_score': 0.0
        }

        try:
            manager = VideoCaptureManager()
            if not manager.open(video_source.device_id,
                              video_source.width,
                              video_source.height,
                              video_source.fps):
                results['error'] = "Failed to open video stream"
                return results

            self.logger.info(f"Testing stream: {video_source.get_display_name()} for {test_duration}s")

            # Test parameters
            frames = []
            timestamps = []
            start_time = time.time()

            # Capture frames for test duration
            while time.time() - start_time < test_duration:
                frame = manager.read_frame()
                if frame is not None:
                    frames.append(frame)
                    timestamps.append(time.time())
                else:
                    self.logger.warning("Failed to capture frame during test")
                    break

                # Small delay to prevent overwhelming
                time.sleep(0.01)

            manager.close()

            if not frames:
                results['error'] = "No frames captured during test"
                return results

            # Calculate metrics
            results['success'] = True
            results['frames_captured'] = len(frames)
            results['resolution'] = (frames[0].shape[1], frames[0].shape[0])  # width, height

            # FPS calculation
            if len(timestamps) > 1:
                time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                avg_frame_time = sum(time_diffs) / len(time_diffs)
                results['avg_fps'] = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

            # Brightness analysis
            brightness_values = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = gray.mean()
                brightness_values.append(brightness)

            results['brightness'] = sum(brightness_values) / len(brightness_values)

            # Stability score (lower variance = more stable)
            if len(brightness_values) > 1:
                variance = sum((x - results['brightness']) ** 2 for x in brightness_values) / len(brightness_values)
                # Normalize to 0-100 scale (lower variance = higher score)
                results['stability_score'] = max(0, 100 - (variance / 10))  # Arbitrary scaling

            self.logger.info(f"Stream test completed: {results['frames_captured']} frames, "
                           f"{results['avg_fps']:.1f} FPS, brightness: {results['brightness']:.1f}")

            return results

        except Exception as e:
            results['error'] = str(e)
            self.logger.error(f"Stream test error: {e}")
            return results

    def quick_test(self, device_id: int) -> bool:
        """Quick test to check if a device is accessible."""
        try:
            manager = VideoCaptureManager()
            success = manager.open(device_id, 640, 480, 30)

            if success:
                # Try to read one frame
                frame = manager.read_frame()
                manager.close()
                return frame is not None
            else:
                return False

        except Exception as e:
            self.logger.error(f"Quick test error for device {device_id}: {e}")
            return False

    def get_optimal_settings(self, video_source: VideoSource) -> Dict:
        """Suggest optimal camera settings based on testing."""
        # Test different resolutions and frame rates
        test_configs = [
            (640, 480, 30),
            (1280, 720, 30),
            (1920, 1080, 30),
            (640, 480, 60),
        ]

        best_config = None
        best_score = 0

        for width, height, fps in test_configs:
            test_source = VideoSource(
                device_id=video_source.device_id,
                name=video_source.name,
                source_type=video_source.source_type,
                width=width,
                height=height,
                fps=fps
            )

            results = self.test_stream(test_source, test_duration=2.0)
            if results['success']:
                # Score based on FPS and stability
                score = results['avg_fps'] * (results['stability_score'] / 100)
                if score > best_score:
                    best_score = score
                    best_config = {
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'score': score
                    }

        if best_config:
            self.logger.info(f"Optimal settings found: {best_config}")
            return best_config
        else:
            # Return default
            return {
                'width': 640,
                'height': 480,
                'fps': 30,
                'score': 0
            }