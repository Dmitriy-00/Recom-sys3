from __future__ import annotations

from bot.recommender import Material, Recommender


def build_material(**kwargs) -> Material:
    defaults = dict(
        title="Test",
        description="",
        modality="практика",
        duration_minutes=10,
        intensity="мягкая",
        tags=("осознанность",),
        url=None,
        language="ru",
    )
    defaults.update(kwargs)
    return Material(**defaults)


def test_recommender_prefers_matching_goal():
    materials = [
        build_material(title="A", tags=("осознанность",)),
        build_material(title="B", tags=("творчество",)),
    ]
    engine = Recommender(materials)

    result = engine.recommend(goal="хочу больше осознанности", limit=1)
    assert result
    assert result[0].material.title == "A"


def test_recommender_filters_by_duration():
    materials = [
        build_material(title="Короткая", duration_minutes=10),
        build_material(title="Длинная", duration_minutes=120),
    ]
    engine = Recommender(materials)

    result = engine.recommend(goal="осознанность", max_duration=30)
    titles = [item.material.title for item in result]
    assert "Короткая" in titles
    assert "Длинная" not in titles


def test_recommender_respects_language():
    materials = [
        build_material(title="Русский", language="ru"),
        build_material(title="English", language="en"),
    ]
    engine = Recommender(materials)

    result = engine.recommend(goal="осознанность", language="ru")
    titles = [item.material.title for item in result]
    assert "Русский" in titles
    assert "English" not in titles
