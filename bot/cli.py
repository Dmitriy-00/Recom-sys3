"""Command line entry point for the transformative materials bot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .data_loader import load_materials
from .recommender import Recommender


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Бот-рекомендатель трансформативных практик и материалов",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "materials.json",
        help="Путь к JSON файлу с материалами",
    )
    parser.add_argument("--goal", help="Какой запрос или намерение сейчас актуально", default=None)
    parser.add_argument(
        "--modality",
        help="Предпочитаемый формат (книга, видео, практика, подкаст и т.п.)",
        default=None,
    )
    parser.add_argument(
        "--max-duration",
        type=int,
        help="Максимальная длительность материала в минутах",
        default=None,
    )
    parser.add_argument(
        "--intensity",
        help="Желаемая интенсивность: мягкая, средняя, глубокая",
        default=None,
    )
    parser.add_argument(
        "--language",
        help="Язык материалов (ru, en и т.п.)",
        default=None,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Количество рекомендаций в выдаче",
    )
    parser.add_argument(
        "--as-json",
        action="store_true",
        help="Вывести результат в формате JSON",
    )
    return parser


def format_recommendations(recommendations: Iterable) -> str:
    blocks = []
    for index, recommendation in enumerate(recommendations, start=1):
        payload = recommendation.as_dict()
        block_lines = [
            f"{index}. {payload['title']} ({payload['modality']}, {payload['duration_minutes']} мин)",
            f"   Интенсивность: {payload['intensity']} | Язык: {payload['language']}",
            f"   Теги: {', '.join(payload['tags']) if payload['tags'] else 'нет'}",
            f"   Описание: {payload['description']}",
        ]
        if payload["url"]:
            block_lines.append(f"   Ссылка: {payload['url']}")
        block_lines.append(f"   Релевантность: {payload['score']}")
        blocks.append("\n".join(block_lines))
    return "\n\n".join(blocks)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    materials = load_materials(args.catalog)
    engine = Recommender(materials)

    recommendations = engine.recommend(
        goal=args.goal,
        modality=args.modality,
        max_duration=args.max_duration,
        intensity=args.intensity,
        language=args.language,
        limit=args.limit,
    )

    if args.as_json:
        payload = [item.as_dict() for item in recommendations]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_recommendations(recommendations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
