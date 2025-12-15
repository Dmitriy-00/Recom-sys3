"""Scoring functions for the explainable recommendation core."""
from __future__ import annotations

from typing import Dict

from .models import MediaItem, UserProfile


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def trope_match(media: MediaItem, user: UserProfile) -> float:
    likes = user.trope_preferences.likes_set()
    dislikes = user.trope_preferences.dislikes_set()
    tropes = media.tropes_set()
    if not tropes:
        return 0.0

    liked_overlap = len(tropes & likes)
    disliked_overlap = len(tropes & dislikes)
    score = _safe_ratio(liked_overlap - disliked_overlap, len(tropes))
    return _clamp(score)


def theme_match(media: MediaItem, user: UserProfile) -> float:
    likes = user.trope_preferences.likes_set()
    dislikes = user.trope_preferences.dislikes_set()
    themes = media.themes_set()
    if not themes:
        return 0.0

    liked_overlap = len(themes & likes)
    disliked_overlap = len(themes & dislikes)
    score = _safe_ratio(liked_overlap - disliked_overlap, len(themes))
    return _clamp(score)


def cognitive_match(media: MediaItem, user: UserProfile) -> float:
    desired = set()
    goals = user.cognitive_goals
    if goals.reflection:
        desired.add("reflection")
    if goals.comfort:
        desired.add("comfort")
    if goals.challenge in {"medium", "high"}:
        desired.add("cognitive_challenge")
    if goals.challenge == "high":
        desired.add("deep_complexity")

    if not desired:
        return 1.0

    overlap = len(media.cognitive_operations_set() & desired)
    return _clamp(_safe_ratio(overlap, len(desired)))


def emotional_fit(media: MediaItem, user: UserProfile) -> float:
    preferred_intensity = {
        "calm": 3,
        "stable": 4,
        "reflective": 5,
        "excited": 8,
        "energized": 7,
    }.get(user.emotional_state.lower(), 5)

    if user.cognitive_goals.comfort and media.emotional_intensity > 7:
        return 0.2

    gap = abs(media.emotional_intensity - preferred_intensity)
    return _clamp(1 - gap / 10)


def novelty(media: MediaItem) -> float:
    return media.normalized_transformative_inverse()


def trope_fatigue_penalty(media: MediaItem, user: UserProfile) -> float:
    penalty_map = {"low": 0.05, "medium": 0.1, "high": 0.2}
    penalty = 0.0
    for trope in media.tropes_set():
        fatigue = user.fatigue_level(trope)
        if fatigue:
            penalty += penalty_map.get(fatigue, 0.0)
    return _clamp(penalty, 0.0, 0.5)


def compute_score(media: MediaItem, user: UserProfile) -> Dict[str, float]:
    """Calculate the full explainable score for a media item."""
    trope_val = trope_match(media, user)
    theme_val = theme_match(media, user)
    cognitive_val = cognitive_match(media, user)
    emotional_val = emotional_fit(media, user)
    novelty_val = novelty(media)
    penalty_val = trope_fatigue_penalty(media, user)

    score = (
        trope_val * 0.30
        + theme_val * 0.20
        + cognitive_val * 0.20
        + emotional_val * 0.20
        + novelty_val * 0.10
        - penalty_val
    )

    score *= media.normalized_annotation()
    score = _clamp(score)

    return {
        "score": score,
        "trope_match": trope_val,
        "theme_match": theme_val,
        "cognitive_match": cognitive_val,
        "emotional_fit": emotional_val,
        "novelty": novelty_val,
        "fatigue_penalty": penalty_val,
        "annotation_confidence": media.normalized_annotation(),
    }
