"""
Configuration manager for Lego Brick Detection application.

Handles persistence of user preferences and detection parameters
to maintain settings across application sessions.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from ..models.detection_params import DetectionParams
from ..models.video_source import VideoSource
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Manages application configuration persistence.

    Provides methods to save and load user preferences, detection parameters,
    and other configurable settings to/from disk.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory to store configuration files.
                       Defaults to user's app data directory.
        """
        if config_dir is None:
            # Use platform-specific app data directory
            home = Path.home()
            if os.name == 'nt':  # Windows
                config_dir = home / 'AppData' / 'Local' / 'LegoBrickDetection'
            else:  # Linux/Mac
                config_dir = home / '.config' / 'lego_brick_detection'

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Configuration file paths
        self.detection_params_file = self.config_dir / 'detection_params.json'
        self.video_source_file = self.config_dir / 'video_source.json'
        self.app_settings_file = self.config_dir / 'app_settings.json'

        logger.info(f"ConfigManager initialized with directory: {self.config_dir}")

    def save_detection_params(self, params: DetectionParams) -> bool:
        """
        Save detection parameters to disk.

        Args:
            params: DetectionParams object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            data = params.to_dict()
            with open(self.detection_params_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Detection parameters saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save detection parameters: {e}")
            return False

    def load_detection_params(self) -> Optional[DetectionParams]:
        """
        Load detection parameters from disk.

        Returns:
            DetectionParams object if successful, None if file doesn't exist or error
        """
        try:
            if not self.detection_params_file.exists():
                logger.info("Detection parameters file does not exist, using defaults")
                return None

            with open(self.detection_params_file, 'r') as f:
                data = json.load(f)

            params = DetectionParams.from_dict(data)
            logger.info("Detection parameters loaded successfully")
            return params
        except Exception as e:
            logger.error(f"Failed to load detection parameters: {e}")
            return None

    def save_video_source(self, video_source: VideoSource) -> bool:
        """
        Save video source configuration to disk.

        Args:
            video_source: VideoSource object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'type': video_source.type,
                'device_id': video_source.device_id,
                'resolution': video_source.resolution,
                'frame_rate': video_source.frame_rate,
                'calibration_data': video_source.calibration_data
            }

            with open(self.video_source_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("Video source configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save video source configuration: {e}")
            return False

    def load_video_source(self) -> Optional[VideoSource]:
        """
        Load video source configuration from disk.

        Returns:
            VideoSource object if successful, None if file doesn't exist or error
        """
        try:
            if not self.video_source_file.exists():
                logger.info("Video source configuration file does not exist")
                return None

            with open(self.video_source_file, 'r') as f:
                data = json.load(f)

            video_source = VideoSource(
                type=data.get('type', 'webcam'),
                device_id=data.get('device_id', 0),
                resolution=tuple(data.get('resolution', [640, 480])),
                frame_rate=data.get('frame_rate', 30),
                calibration_data=data.get('calibration_data')
            )

            logger.info("Video source configuration loaded successfully")
            return video_source
        except Exception as e:
            logger.error(f"Failed to load video source configuration: {e}")
            return None

    def save_app_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save general application settings to disk.

        Args:
            settings: Dictionary of application settings

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.app_settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Application settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save application settings: {e}")
            return False

    def load_app_settings(self) -> Dict[str, Any]:
        """
        Load general application settings from disk.

        Returns:
            Dictionary of settings, empty dict if file doesn't exist or error
        """
        try:
            if not self.app_settings_file.exists():
                logger.info("Application settings file does not exist")
                return {}

            with open(self.app_settings_file, 'r') as f:
                settings = json.load(f)

            logger.info("Application settings loaded successfully")
            return settings
        except Exception as e:
            logger.error(f"Failed to load application settings: {e}")
            return {}

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the current configuration state.

        Returns:
            Dictionary with configuration file paths and existence status
        """
        return {
            'config_directory': str(self.config_dir),
            'detection_params_exists': self.detection_params_file.exists(),
            'video_source_exists': self.video_source_file.exists(),
            'app_settings_exists': self.app_settings_file.exists(),
            'detection_params_path': str(self.detection_params_file),
            'video_source_path': str(self.video_source_file),
            'app_settings_path': str(self.app_settings_file)
        }

    def reset_all_configs(self) -> bool:
        """
        Delete all configuration files, resetting to defaults.

        Returns:
            True if all files deleted successfully
        """
        try:
            files_to_delete = [
                self.detection_params_file,
                self.video_source_file,
                self.app_settings_file
            ]

            for file_path in files_to_delete:
                if file_path.exists():
                    file_path.unlink()

            logger.info("All configuration files reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset configuration files: {e}")
            return False