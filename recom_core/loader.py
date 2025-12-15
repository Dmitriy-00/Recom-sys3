"""CSV loader for media items exported from the Obsidian semantic core."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .models import MediaItem, MediaType


REQUIRED_COLUMNS = {
    "id",
    "type",
    "title",
    "year",
    "genres",
    "themes",
    "tropes",
    "core_concepts",
    "transformative_score",
    "cognitive_operations",
    "difficulty_level",
    "emotional_intensity",
    "moral_ambiguity",
    "accessibility",
    "trigger_warnings",
    "annotation_confidence",
}


def _split_list(raw: str) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.replace(";", ",").split(",") if item.strip()]


def load_media_csv(path: str | Path) -> List[MediaItem]:
    """
    Load media items from a CSV file.

    The CSV must contain columns matching the semantic media entity
    fields. List-like fields can be comma- or semicolon-separated.
    """
    items: List[MediaItem] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")

        for row in reader:
            items.append(
                MediaItem(
                    id=row["id"],
                    type=MediaType(row["type"].strip().lower()),
                    title=row["title"],
                    year=int(row["year"]),
                    genres=_split_list(row.get("genres", "")),
                    themes=_split_list(row.get("themes", "")),
                    tropes=_split_list(row.get("tropes", "")),
                    core_concepts=_split_list(row.get("core_concepts", "")),
                    transformative_score=int(row["transformative_score"]),
                    cognitive_operations=_split_list(row.get("cognitive_operations", "")),
                    difficulty_level=int(row["difficulty_level"]),
                    emotional_intensity=int(row["emotional_intensity"]),
                    moral_ambiguity=float(row["moral_ambiguity"]),
                    accessibility=int(row["accessibility"]),
                    trigger_warnings=_split_list(row.get("trigger_warnings", "")),
                    annotation_confidence=int(row["annotation_confidence"]),
                )
            )
    return items


def load_multiple(paths: Iterable[str | Path]) -> List[MediaItem]:
    """Load media items from multiple CSV files into a single list."""
    items: List[MediaItem] = []
    for path in paths:
        items.extend(load_media_csv(path))
    return items
