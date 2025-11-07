"""Recommendation engine for transformative learning materials."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import statistics
from typing import Iterable, List, Mapping, Sequence


@dataclass(slots=True)
class Material:
    """A single learning or practice material."""

    title: str
    description: str
    modality: str
    duration_minutes: int
    intensity: str
    tags: Sequence[str] = field(default_factory=tuple)
    url: str | None = None
    language: str = "ru"

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "Material":
        """Create a :class:`Material` from a mapping."""

        tags = payload.get("tags", [])
        if isinstance(tags, str):
            tags = [piece.strip() for piece in tags.split(",") if piece.strip()]
        return cls(
            title=str(payload["title"]),
            description=str(payload.get("description", "")),
            modality=str(payload.get("modality", "unspecified")),
            duration_minutes=int(payload.get("duration_minutes", 0)),
            intensity=str(payload.get("intensity", "мягкая")),
            tags=tuple(str(tag).lower() for tag in tags),
            url=str(payload.get("url")) if payload.get("url") else None,
            language=str(payload.get("language", "ru")).lower(),
        )


class Recommendation:
    """A result returned by the recommender engine."""

    def __init__(self, material: Material, score: float) -> None:
        self.material = material
        self.score = score

    def as_dict(self) -> dict:
        return {
            "title": self.material.title,
            "description": self.material.description,
            "modality": self.material.modality,
            "duration_minutes": self.material.duration_minutes,
            "intensity": self.material.intensity,
            "tags": list(self.material.tags),
            "url": self.material.url,
            "language": self.material.language,
            "score": round(self.score, 2),
        }


class Recommender:
    """Score and rank materials according to the user's intention."""

    def __init__(self, materials: Iterable[Material]):
        self._materials: List[Material] = list(materials)
        if not self._materials:
            raise ValueError("Список материалов не может быть пустым")

    def recommend(
        self,
        *,
        goal: str | None = None,
        modality: str | None = None,
        max_duration: int | None = None,
        intensity: str | None = None,
        language: str | None = None,
        limit: int = 5,
    ) -> List[Recommendation]:
        """Return ranked recommendations based on the provided preferences."""

        scored: List[Recommendation] = []
        for material in self._materials:
            score = self._score_material(
                material,
                goal=goal,
                modality=modality,
                max_duration=max_duration,
                intensity=intensity,
                language=language,
            )
            if score <= 0:
                continue
            scored.append(Recommendation(material, score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def _score_material(
        self,
        material: Material,
        *,
        goal: str | None,
        modality: str | None,
        max_duration: int | None,
        intensity: str | None,
        language: str | None,
    ) -> float:
        score = 0.0

        if goal:
            score += self._goal_score(goal, material.tags, material.description)

        if modality and modality.lower() == material.modality.lower():
            score += 2.0

        if max_duration is not None:
            if material.duration_minutes <= max_duration:
                score += 1.5
            else:
                return 0.0

        if intensity:
            if intensity.lower() == material.intensity.lower():
                score += 1.0
            else:
                score -= 0.5

        if language and language.lower() != material.language:
            return 0.0

        # Prefer balanced durations (avoid extremes) when the user has no
        # explicit limit. Encourages varied experiences.
        if max_duration is None:
            durations = [item.duration_minutes for item in self._materials if item.duration_minutes]
            if durations:
                median = statistics.median(durations)
                deviation = abs(material.duration_minutes - median)
                score += max(0.0, 1.0 - deviation / (median + 1))

        return round(score, 4)

    @staticmethod
    def _goal_score(goal: str, tags: Sequence[str], description: str) -> float:
        """Compute a similarity score between the goal and material metadata."""

        goal_tokens = _tokenize(goal)
        if not goal_tokens:
            return 0.0

        tag_tokens = set(tags)
        description_tokens = set(_tokenize(description))

        overlap = goal_tokens & (tag_tokens | description_tokens)
        if not overlap:
            return 0.0

        coverage = len(overlap) / len(goal_tokens)
        boost = 1.0 + math.log1p(len(overlap))
        return coverage * 3.0 * boost


def _tokenize(text: str) -> set[str]:
    return {token for token in _normalize(text).split(" ") if token}


def _normalize(text: str) -> str:
    return (
        text.lower()
        .replace(",", " ")
        .replace(".", " ")
        .replace("!", " ")
        .replace("?", " ")
        .replace("-", " ")
    )
