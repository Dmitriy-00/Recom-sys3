"""Recommendation pipeline that applies filters, scoring, and ranking."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .models import MediaItem, UserProfile
from .scoring import compute_score


@dataclass
class Recommendation:
    media_id: str
    title: str
    score: float
    explain: Dict[str, float]
    warnings: List[str]


class RecommendationEngine:
    """Deterministic, rule-based recommendation engine."""

    def __init__(self, catalog: List[MediaItem]):
        self.catalog = catalog

    def _passes_filters(self, media: MediaItem, user: UserProfile) -> Tuple[bool, List[str]]:
        warnings: List[str] = []
        triggers = media.trigger_warnings_set()
        blocked_triggers = user.avoid_triggers_set()
        if triggers & blocked_triggers:
            return False, warnings

        comfort_level = max(1, int(user.experience_level * 10))
        if media.difficulty_level > comfort_level + 2:
            return False, warnings

        min_accessibility = 4 if user.experience_level < 0.4 else 2 if user.experience_level < 0.7 else 1
        if media.accessibility < min_accessibility:
            return False, warnings

        if media.emotional_intensity > 8 and user.cognitive_goals.comfort:
            warnings.append("high_emotional_intensity")
        if media.moral_ambiguity > 0.8:
            warnings.append("moral_ambiguity")
        return True, warnings

    def recommend(self, user: UserProfile, limit: int = 5) -> List[Recommendation]:
        candidates: List[Tuple[MediaItem, Dict[str, float], List[str]]] = []
        for media in self.catalog:
            allowed, warnings = self._passes_filters(media, user)
            if not allowed:
                continue
            explain = compute_score(media, user)
            candidates.append((media, explain, warnings))

        ranked = sorted(candidates, key=lambda item: item[1]["score"], reverse=True)

        results: List[Recommendation] = []
        for media, explain, warnings in ranked[:limit]:
            results.append(
                Recommendation(
                    media_id=media.id,
                    title=media.title,
                    score=explain["score"],
                    explain=explain,
                    warnings=warnings,
                )
            )
        return results
