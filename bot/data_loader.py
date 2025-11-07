"""Utilities for loading the catalog of transformative materials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .recommender import Material


def load_materials(path: str | Path) -> List[Material]:
    """Load a list of :class:`Material` objects from a JSON file.

    Parameters
    ----------
    path:
        Path to the JSON file. The file must contain an array of objects with
        the same keys as :class:`Material` fields.

    Returns
    -------
    list of Material
        Parsed materials ready to be consumed by the recommender engine.
    """

    path = Path(path)
    with path.open("r", encoding="utf-8") as stream:
        payload: Iterable[dict] = json.load(stream)

    materials: List[Material] = [Material.from_mapping(raw) for raw in payload]
    return materials
