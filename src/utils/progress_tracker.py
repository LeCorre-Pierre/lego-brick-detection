"""
Progress tracking system for Lego Brick Detection application.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..models.lego_set import LegoSet
from ..models.brick import Brick
from ..utils.logger import get_logger

logger = get_logger("progress_tracker")

class ProgressTracker:
    """Tracks progress of finding bricks in a Lego set."""

    def __init__(self):
        self.logger = logger
        self.current_set = None
        self.start_time = None
        self.last_activity = None
        self.found_history = []  # List of (timestamp, brick_id) tuples

    def start_tracking(self, lego_set: LegoSet):
        """Start tracking progress for a Lego set."""
        self.current_set = lego_set
        self.start_time = datetime.now()
        self.last_activity = self.start_time
        self.found_history.clear()
        self.logger.info(f"Started tracking progress for set: {lego_set.name}")

    def stop_tracking(self):
        """Stop tracking progress."""
        if self.start_time:
            duration = datetime.now() - self.start_time
            self.logger.info(f"Stopped tracking after {duration}")
        self.current_set = None
        self.start_time = None
        self.last_activity = None

    def record_brick_found(self, brick_id: str):
        """Record that a brick was found."""
        if not self.current_set:
            return

        timestamp = datetime.now()
        self.found_history.append((timestamp, brick_id))
        self.last_activity = timestamp

        self.logger.debug(f"Recorded brick found: {brick_id}")

    def get_progress_stats(self) -> Dict:
        """Get current progress statistics."""
        if not self.current_set:
            return {}

        total_bricks = self.current_set.total_bricks
        found_bricks = self.current_set.get_found_bricks_count()
        completion_percentage = (found_bricks / total_bricks * 100) if total_bricks > 0 else 0

        stats = {
            'total_bricks': total_bricks,
            'found_bricks': found_bricks,
            'remaining_bricks': total_bricks - found_bricks,
            'completion_percentage': completion_percentage,
            'is_complete': self.current_set.is_complete(),
            'bricks_found_today': self._get_bricks_found_in_last_24h(),
            'average_bricks_per_hour': self._get_average_bricks_per_hour(),
            'time_elapsed': self._get_time_elapsed(),
            'estimated_completion_time': self._get_estimated_completion_time()
        }

        return stats

    def get_brick_progress(self) -> List[Dict]:
        """Get progress for each individual brick type."""
        if not self.current_set:
            return []

        progress = []
        for brick in self.current_set.bricks:
            brick_stats = {
                'id': brick.part_number,
                'name': brick.name if hasattr(brick, 'name') else f"Brick {brick.part_number}",
                'quantity': brick.quantity,
                'found_quantity': brick.found_quantity,
                'remaining_quantity': brick.get_remaining_quantity(),
                'is_complete': brick.is_fully_found(),
                'progress_percentage': (brick.found_quantity / brick.quantity * 100) if brick.quantity > 0 else 0
            }
            progress.append(brick_stats)

        return progress

    def _get_bricks_found_in_last_24h(self) -> int:
        """Get number of bricks found in the last 24 hours."""
        if not self.found_history:
            return 0

        cutoff = datetime.now() - timedelta(hours=24)
        recent_finds = [f for f in self.found_history if f[0] >= cutoff]
        return len(recent_finds)

    def _get_average_bricks_per_hour(self) -> float:
        """Calculate average bricks found per hour."""
        if not self.start_time or not self.found_history:
            return 0.0

        elapsed_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        if elapsed_hours <= 0:
            return 0.0

        return len(self.found_history) / elapsed_hours

    def _get_time_elapsed(self) -> str:
        """Get formatted time elapsed since tracking started."""
        if not self.start_time:
            return "00:00:00"

        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _get_estimated_completion_time(self) -> Optional[str]:
        """Estimate time to completion based on current rate."""
        if not self.current_set or not self.found_history:
            return None

        remaining_bricks = self.current_set.total_bricks - self.current_set.get_found_bricks_count()
        if remaining_bricks <= 0:
            return "Complete"

        avg_per_hour = self._get_average_bricks_per_hour()
        if avg_per_hour <= 0:
            return "Unknown"

        hours_remaining = remaining_bricks / avg_per_hour
        if hours_remaining < 1:
            minutes_remaining = int(hours_remaining * 60)
            return f"{minutes_remaining} minutes"
        elif hours_remaining < 24:
            return f"{hours_remaining:.1f} hours"
        else:
            days_remaining = hours_remaining / 24
            return f"{days_remaining:.1f} days"

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent brick finding activity."""
        recent = self.found_history[-limit:] if self.found_history else []
        activity = []

        for timestamp, brick_id in recent:
            activity.append({
                'timestamp': timestamp.isoformat(),
                'brick_id': brick_id,
                'time_ago': self._format_time_ago(timestamp)
            })

        return activity

    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format a timestamp as time ago."""
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return f"{diff.seconds} seconds ago"