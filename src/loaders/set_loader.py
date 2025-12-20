"""
Set loader for parsing Lego set data from Rebrickable CSV files.
"""

import csv
import logging
from pathlib import Path
from typing import Optional
from ..models.lego_set import LegoSet
from ..models.brick import Brick
from ..utils.logger import get_logger

logger = get_logger("set_loader")

class SetLoader:
    """Loads Lego set data from Rebrickable CSV format."""

    def __init__(self):
        self.logger = logger

    def load_from_csv(self, file_path: str) -> Optional[LegoSet]:
        """
        Load a Lego set from a Rebrickable CSV file.

        Expected CSV format for parts:
        set_num,part_num,color_id,color_name,quantity,is_spare

        Expected CSV format for sets:
        set_num,name,year,theme_id,num_parts
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # First, try to read set info (if available)
            set_info = self._read_set_info(path)

            # Read parts data
            bricks = self._read_parts_data(path)

            if not bricks:
                raise ValueError("No valid brick data found in CSV")

            # Create LegoSet
            set_name = set_info.get('name', f"Set {set_info.get('set_num', 'Unknown')}")
            set_number = set_info.get('set_num', 'unknown')
            total_bricks = sum(brick.quantity for brick in bricks)

            lego_set = LegoSet(
                name=set_name,
                set_number=set_number,
                total_bricks=total_bricks,
                bricks=bricks
            )

            self.logger.info(f"Loaded set '{set_name}' with {len(bricks)} brick types ({total_bricks} total bricks)")
            return lego_set

        except Exception as e:
            self.logger.error(f"Failed to load set from {file_path}: {e}")
            raise

    def _read_set_info(self, path: Path) -> dict:
        """Read set information from CSV (first row or separate file)."""
        # For simplicity, assume set info is in the parts file or derive from filename
        # In a real implementation, might have separate set CSV
        set_num = path.stem  # Use filename as set number
        return {'set_num': set_num, 'name': f'Set {set_num}'}

    def _read_parts_data(self, path: Path) -> list[Brick]:
        """Read parts data from CSV."""
        bricks = []

        with open(path, 'r', encoding='utf-8') as csvfile:
            # Try to detect if header is present
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)

            reader = csv.DictReader(csvfile) if has_header else csv.reader(csvfile)

            for row in reader:
                try:
                    if has_header:
                        brick = self._parse_brick_from_dict(row)
                    else:
                        brick = self._parse_brick_from_list(row)

                    if brick:
                        bricks.append(brick)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Skipping invalid row: {row} - {e}")
                    continue

        return bricks

    def _parse_brick_from_dict(self, row: dict) -> Optional[Brick]:
        """Parse brick from dictionary (header present)."""
        try:
            part_num = row.get('part_num', row.get('Part Num', ''))
            color = row.get('color_name', row.get('Color Name', 'Unknown'))
            quantity = int(row.get('quantity', row.get('Quantity', 1)))
            is_spare = row.get('is_spare', row.get('Is Spare', 'f')).lower() in ('true', 't', '1')

            if not part_num or quantity < 1:
                return None

            # Skip spare parts for now
            if is_spare:
                return None

            return Brick(
                part_number=part_num,
                color=color,
                quantity=quantity
            )
        except (ValueError, TypeError):
            return None

    def _parse_brick_from_list(self, row: list) -> Optional[Brick]:
        """Parse brick from list (no header)."""
        # Assume format: set_num, part_num, color_id, color_name, quantity, is_spare
        if len(row) < 5:
            return None

        try:
            part_num = row[1]
            color = row[3]
            quantity = int(row[4])

            if not part_num or quantity < 1:
                return None

            return Brick(
                part_number=part_num,
                color=color,
                quantity=quantity
            )
        except (ValueError, IndexError):
            return None