"""Data models for the transformative media recommendation system.

This module defines the structured representations for media items,
user profiles, and controlled vocabularies. The data model mirrors the
YAML definitions from the semantic core and is intentionally explicit to
keep the recommendation pipeline deterministic and explainable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class MediaType(str, Enum):
    FILM = "film"
    BOOK = "book"
    GAME = "game"


class ProfileType(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    WALKER = "walker"


@dataclass
class TropePreferences:
    """Explicit likes and dislikes for tropes or thematic elements."""

    likes: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)

    def likes_set(self) -> Set[str]:
        return {item.strip().lower() for item in self.likes if item}

    def dislikes_set(self) -> Set[str]:
        return {item.strip().lower() for item in self.dislikes if item}


@dataclass
class CognitiveGoals:
    """Cognitive and emotional intentions provided by the user."""

    reflection: bool
    challenge: str  # low | medium | high
    comfort: bool


@dataclass
class UserProfile:
    """User profile aligned with the semantic data model."""

    user_id: str
    profile_type: ProfileType
    experience_level: float  # 0-1
    genre_literacy: Dict[str, float]
    trope_preferences: TropePreferences
    trope_fatigue: Dict[str, str]  # trope -> low | medium | high
    emotional_state: str
    cognitive_goals: CognitiveGoals
    avoid_triggers: List[str] = field(default_factory=list)

    def fatigue_level(self, trope: str) -> str | None:
        return self.trope_fatigue.get(trope.lower())

    def avoid_triggers_set(self) -> Set[str]:
        return {trigger.strip().lower() for trigger in self.avoid_triggers if trigger}


@dataclass
class MediaItem:
    """Media entity exported from the Obsidian semantic core."""

    id: str
    type: MediaType
    title: str
    year: int
    genres: List[str]
    themes: List[str]
    tropes: List[str]
    core_concepts: List[str]
    transformative_score: int  # 0-10
    cognitive_operations: List[str]
    difficulty_level: int  # 1-10
    emotional_intensity: int  # 1-10
    moral_ambiguity: float  # 0-1
    accessibility: int  # 1-10
    trigger_warnings: List[str]
    annotation_confidence: int  # 1-10

    def normalized_annotation(self) -> float:
        return max(1, min(self.annotation_confidence, 10)) / 10

    def normalized_transformative_inverse(self) -> float:
        return max(0.0, min(10.0, 10 - self.transformative_score)) / 10

    def genres_set(self) -> Set[str]:
        return {g.lower() for g in self.genres}

    def themes_set(self) -> Set[str]:
        return {t.lower() for t in self.themes}

    def tropes_set(self) -> Set[str]:
        return {t.lower() for t in self.tropes}

    def cognitive_operations_set(self) -> Set[str]:
        return {c.lower() for c in self.cognitive_operations}

    def trigger_warnings_set(self) -> Set[str]:
        return {w.lower() for w in self.trigger_warnings}
