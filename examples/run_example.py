"""Example usage of the explainable recommendation engine."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from recom_core import (
    CognitiveGoals,
    ProfileType,
    RecommendationEngine,
    TropePreferences,
    UserProfile,
    load_media_csv,
)


def main() -> None:
    catalog = load_media_csv("data/sample_media.csv")

    user = UserProfile(
        user_id="analyst_1",
        profile_type=ProfileType.ANALYST,
        experience_level=0.6,
        genre_literacy={"sci-fi": 0.7, "art": 0.5, "puzzle": 0.6},
        trope_preferences=TropePreferences(
            likes=["reflection", "cognitive_challenge", "heist", "existentialism"],
            dislikes=["violence"],
        ),
        trope_fatigue={"heist": "medium"},
        avoid_triggers=["violence"],
        emotional_state="reflective",
        cognitive_goals=CognitiveGoals(reflection=True, challenge="high", comfort=False),
    )

    engine = RecommendationEngine(catalog)
    recommendations = engine.recommend(user, limit=3)

    for rec in recommendations:
        print(f"{rec.title} ({rec.media_id}) -> {rec.score:.3f}")
        for key, value in rec.explain.items():
            print(f"  {key}: {value:.3f}")
        if rec.warnings:
            print(f"  warnings: {', '.join(rec.warnings)}")
        print("-")


if __name__ == "__main__":
    main()
