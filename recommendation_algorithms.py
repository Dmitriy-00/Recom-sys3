#!/usr/bin/env python3
"""
Рекомендательный бот на основе трансформативных материалов
Примеры реализации основных алгоритмов

Версия: 1.0
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math


# ============================================================================
# СТРУКТУРЫ ДАННЫХ
# ============================================================================

class TropeUsageType(Enum):
    """Типы использования тропов"""
    STRAIGHT = "straight"
    DECONSTRUCTION = "deconstruction"
    SUBVERSION = "subversion"
    RECONSTRUCTION = "reconstruction"
    META = "meta"
    LAMPSHADE = "lampshade"


@dataclass
class TropeAnalysis:
    """Анализ одного тропа в материале"""
    trope_id: str
    usage_type: TropeUsageType
    execution: int  # 1-10
    transformation_potential: int  # 1-10
    requires_literacy: int  # 1-10
    notes: str = ""


@dataclass
class Material:
    """Профиль материала"""
    id: str
    title: str
    type: str  # film, book, series
    year: int
    creator: List[str]
    genre: List[str]
    
    # Оценки
    complexity: int  # 1-10
    transformation_score: int  # 1-10
    emotional_intensity: int  # 1-10
    
    # Когнитивные требования
    meta_awareness: int  # 1-10
    intertextual_knowledge: int  # 1-10
    requires_genre_literacy: int  # 1-10
    
    # Анализ тропов
    analyzed_tropes: List[TropeAnalysis]
    
    # Трансформативные механизмы
    transformation_mechanisms: List[str]


@dataclass
class User:
    """Профиль пользователя"""
    id: str
    
    # Текущий уровень
    complexity_tolerance: int  # 1-10
    meta_awareness_level: int  # 1-10
    
    # Работа с тропами
    tolerance_for_deconstruction: int  # 1-10
    needs_reconstruction: int  # 1-10
    trope_fatigue: List[str]
    trope_interest: List[str]
    enjoys_meta: bool
    
    # Жанровая грамотность
    genre_literacy: Dict[str, int]  # genre -> level (1-10)
    
    # Предпочтения
    favorite_genres: List[str]
    disliked_genres: List[str]


# ============================================================================
# АЛГОРИТМ 1: ОЦЕНКА РАБОТЫ С ТРОПАМИ
# ============================================================================

def match_trope_engagement(material: Material, user: User) -> Dict[str, Any]:
    """
    Оценивает, готов ли пользователь к тому, как материал работает с тропами
    
    Returns:
        Dict с оценкой (0-10) и деталями
    """
    score = 10.0
    details = []
    
    for trope in material.analyzed_tropes:
        # 1. Знает ли пользователь этот троп?
        user_knows_trope = trope.trope_id not in user.trope_fatigue
        requires_knowledge = trope.requires_literacy >= 7
        
        if requires_knowledge and not user_knows_trope:
            score -= 2
            details.append(
                f"Деконструкция {trope.trope_id} требует знания оригинала"
            )
        
        # 2. Готов ли к типу использования?
        if trope.usage_type == TropeUsageType.DECONSTRUCTION:
            tolerance = user.tolerance_for_deconstruction
            if tolerance < 5:
                score -= 2
                details.append("Деконструкция может расстроить")
        
        # 3. Усталость от тропа?
        if trope.trope_id in user.trope_fatigue:
            if trope.usage_type == TropeUsageType.STRAIGHT:
                score -= 3
                details.append(
                    f"Усталость от прямого использования {trope.trope_id}"
                )
            elif trope.usage_type in [
                TropeUsageType.DECONSTRUCTION,
                TropeUsageType.SUBVERSION
            ]:
                score += 1
                details.append(
                    f"Свежий взгляд на надоевший {trope.trope_id}"
                )
        
        # 4. Метауровень доступен?
        if trope.usage_type == TropeUsageType.META:
            if not user.enjoys_meta:
                score -= 2
                details.append("Метакомментарий может быть непонятен")
            if user.meta_awareness_level < 7:
                score -= 1
                details.append("Низкий уровень мета-осознанности")
    
    # 5. Нужна ли реконструкция после деконструкции?
    if user.needs_reconstruction >= 7:
        has_only_deconstruction = all(
            t.usage_type == TropeUsageType.DECONSTRUCTION
            for t in material.analyzed_tropes
        )
        if has_only_deconstruction:
            score -= 1
            details.append("Много деконструкции без восстановления")
    
    # Нормализуем оценку
    score = max(0, min(10, score))
    
    return {
        'score': score,
        'details': details,
        'learning_opportunity': score >= 7 and score <= 9
    }


# ============================================================================
# АЛГОРИТМ 2: ЗОНА БЛИЖАЙШЕГО РАЗВИТИЯ
# ============================================================================

def is_in_zpd(material: Material, user: User) -> Dict[str, Any]:
    """
    Проверяет, находится ли материал в зоне ближайшего развития (ZPD)
    
    Returns:
        Dict с информацией о соответствии зоне развития
    """
    material_complexity = material.complexity
    user_level = user.complexity_tolerance
    
    # Идеальная зона: +1 или +2 от текущего уровня
    if user_level <= material_complexity <= user_level + 2:
        return {
            'in_zpd': True,
            'challenge_level': 'optimal',
            'growth_potential': 'high',
            'recommendation': 'Идеально для роста'
        }
    
    # Слишком простой
    elif material_complexity < user_level - 1:
        return {
            'in_zpd': False,
            'challenge_level': 'too_easy',
            'growth_potential': 'low',
            'recommendation': 'Только для комфортного просмотра'
        }
    
    # Слишком сложный
    elif material_complexity > user_level + 3:
        return {
            'in_zpd': False,
            'challenge_level': 'too_hard',
            'growth_potential': 'blocked',
            'recommendation': 'Требуются промежуточные шаги',
            'gap': material_complexity - user_level
        }
    
    # Умеренная зона (+3)
    else:
        return {
            'in_zpd': True,
            'challenge_level': 'moderate',
            'growth_potential': 'medium',
            'recommendation': 'Сложновато, но можно справиться'
        }


# ============================================================================
# АЛГОРИТМ 3: ИТОГОВАЯ ОЦЕНКА СООТВЕТСТВИЯ
# ============================================================================

def calculate_content_fit(material: Material, user: User) -> float:
    """Оценка контентного соответствия (0-10)"""
    score = 5.0
    
    # Совпадение жанров
    genre_overlap = len(set(material.genre) & set(user.favorite_genres))
    score += genre_overlap * 1.5
    
    # Нежелательные жанры
    genre_conflict = len(set(material.genre) & set(user.disliked_genres))
    score -= genre_conflict * 3
    
    return max(0, min(10, score))


def calculate_structural_fit(material: Material, user: User) -> float:
    """Оценка структурного соответствия (0-10)"""
    score = 5.0
    
    # Сложность в зоне комфорта?
    complexity_diff = abs(material.complexity - user.complexity_tolerance)
    if complexity_diff <= 2:
        score += 3
    elif complexity_diff <= 4:
        score += 1
    else:
        score -= 2
    
    # Мета-осознанность
    meta_diff = abs(material.meta_awareness - user.meta_awareness_level)
    if meta_diff <= 2:
        score += 2
    elif meta_diff > 4:
        score -= 2
    
    return max(0, min(10, score))


def calculate_recommendation_score(
    material: Material, 
    user: User
) -> Dict[str, Any]:
    """
    Вычисляет итоговую оценку соответствия материала пользователю
    
    Returns:
        Dict с финальной оценкой и разбивкой по компонентам
    """
    # Компоненты оценки
    content_fit = calculate_content_fit(material, user)
    structural_fit = calculate_structural_fit(material, user)
    
    trope_result = match_trope_engagement(material, user)
    trope_engagement_fit = trope_result['score']
    
    # Трансформативный потенциал с учётом тропов
    base_transformation = material.transformation_score
    
    # Бонус за глубокую работу с тропами
    high_quality_tropes = [
        t for t in material.analyzed_tropes 
        if t.execution >= 7 and t.transformation_potential >= 7
    ]
    trope_bonus = min(2, len(high_quality_tropes) * 0.5)
    
    adjusted_transformation = min(10, base_transformation + trope_bonus)
    
    # Итоговая формула
    final_score = (
        content_fit * 0.30 +
        structural_fit * 0.30 +
        trope_engagement_fit * 0.20 +
        adjusted_transformation * 0.20
    )
    
    return {
        'score': round(final_score, 2),
        'breakdown': {
            'content': round(content_fit, 2),
            'structure': round(structural_fit, 2),
            'trope_work': round(trope_engagement_fit, 2),
            'transformation': round(adjusted_transformation, 2)
        },
        'trope_details': trope_result['details'],
        'growth_opportunity': trope_result['learning_opportunity'],
        'zpd_info': is_in_zpd(material, user)
    }


# ============================================================================
# АЛГОРИТМ 4: ПОСТРОЕНИЕ ТРЕКА РАЗВИТИЯ
# ============================================================================

def build_learning_track(
    user: User,
    goal_material: Material,
    materials_db: List[Material]
) -> Dict[str, Any]:
    """
    Строит последовательность материалов от текущего уровня 
    до целевого сложного материала
    
    Args:
        user: Профиль пользователя
        goal_material: Целевой материал
        materials_db: База всех доступных материалов
    
    Returns:
        Dict с треком и объяснениями
    """
    current_level = user.complexity_tolerance
    goal_level = goal_material.complexity
    gap = goal_level - current_level
    
    # Если разрыв маленький - можно сразу
    if gap <= 2:
        return {
            'track': [goal_material],
            'estimated_weeks': 1,
            'explanation': 'Вы готовы к этому материалу!'
        }
    
    # Вычисляем количество шагов (примерно +1.5 за шаг)
    steps_needed = math.ceil(gap / 1.5)
    
    track = []
    explanations = []
    
    for step in range(steps_needed):
        # Целевая сложность для этого шага
        target_complexity = current_level + (step + 1) * 1.5
        
        # Ищем подходящий материал
        candidates = [
            m for m in materials_db
            if abs(m.complexity - target_complexity) <= 0.5
            and any(g in m.genre for g in goal_material.genre)
            and m.id != goal_material.id
            and m.id not in [t.id for t in track]
        ]
        
        if not candidates:
            continue
        
        # Выбираем лучшего кандидата
        best = max(candidates, key=lambda m: m.transformation_score)
        track.append(best)
        
        explanations.append({
            'step': step + 1,
            'material': best.title,
            'complexity': best.complexity,
            'purpose': f'Подготовка к сложности {target_complexity}'
        })
    
    # Добавляем целевой материал
    track.append(goal_material)
    explanations.append({
        'step': len(track),
        'material': goal_material.title,
        'complexity': goal_material.complexity,
        'purpose': 'Достижение цели'
    })
    
    return {
        'track': track,
        'steps': explanations,
        'estimated_weeks': len(track) * 2,
        'explanation': f'Путь из {len(track)} шагов к цели'
    }


# ============================================================================
# АЛГОРИТМ 5: ОБНОВЛЕНИЕ ПРОФИЛЯ ПОСЛЕ ПРОСМОТРА
# ============================================================================

def update_user_profile(
    user: User,
    material: Material,
    rating: int,  # 1-5
    feedback: Dict[str, Any]
) -> User:
    """
    Обновляет профиль пользователя на основе обратной связи
    
    Args:
        user: Профиль пользователя
        material: Просмотренный материал
        rating: Оценка (1-5)
        feedback: Словарь с дополнительной обратной связью
    
    Returns:
        Обновлённый профиль пользователя
    """
    # Если материал понравился (4-5 звёзд)
    if rating >= 4:
        # 1. Повышаем толерантность к типам тропов
        for trope in material.analyzed_tropes:
            if trope.usage_type == TropeUsageType.DECONSTRUCTION:
                user.tolerance_for_deconstruction = min(
                    10,
                    user.tolerance_for_deconstruction + 0.2
                )
            
            # Снимаем усталость при качественном использовании
            if trope.trope_id in user.trope_fatigue:
                if trope.execution >= 7:
                    user.trope_fatigue.remove(trope.trope_id)
                    user.trope_interest.append(trope.trope_id)
        
        # 2. Повышаем мета-осознанность
        if material.meta_awareness > user.meta_awareness_level:
            user.meta_awareness_level = min(
                10,
                user.meta_awareness_level + 0.3
            )
        
        # 3. Обновляем жанровую грамотность
        for genre in material.genre:
            current = user.genre_literacy.get(genre, 0)
            user.genre_literacy[genre] = min(10, current + 0.5)
        
        # 4. Повышаем толерантность к сложности
        if material.complexity > user.complexity_tolerance:
            user.complexity_tolerance = min(
                10,
                user.complexity_tolerance + 0.2
            )
    
    # Если не понравился (1-2 звезды)
    elif rating <= 2:
        # Анализируем причины
        complaints = feedback.get('complaints', [])
        
        if 'too_complex' in complaints:
            # Снижаем порог сложности
            user.complexity_tolerance = max(
                1,
                user.complexity_tolerance - 0.3
            )
        
        if 'boring' in complaints:
            # Повышаем минимальный интерес
            user.complexity_tolerance = min(
                10,
                user.complexity_tolerance + 0.2
            )
        
        # Добавляем троп в усталость
        disliked_trope = feedback.get('disliked_trope')
        if disliked_trope and disliked_trope not in user.trope_fatigue:
            user.trope_fatigue.append(disliked_trope)
    
    # Отмечаем прорыв
    if feedback.get('breakthrough'):
        # Сильное повышение мета-осознанности
        user.meta_awareness_level = min(
            10,
            user.meta_awareness_level + 0.5
        )
    
    return user


# ============================================================================
# АЛГОРИТМ 6: ПОИСК РЕКОМЕНДАЦИЙ
# ============================================================================

def find_recommendations(
    user: User,
    materials_db: List[Material],
    n: int = 5,
    context: Dict[str, Any] = None
) -> List[Tuple[Material, Dict[str, Any]]]:
    """
    Находит топ-N рекомендаций для пользователя
    
    Args:
        user: Профиль пользователя
        materials_db: База материалов
        n: Количество рекомендаций
        context: Дополнительный контекст (настроение, время и т.д.)
    
    Returns:
        Список пар (материал, объяснение)
    """
    scored_materials = []
    
    for material in materials_db:
        result = calculate_recommendation_score(material, user)
        
        # Учитываем контекст
        if context:
            # Если мало времени - исключаем длинные
            if context.get('time_available') == 'short':
                if material.type == 'series':
                    result['score'] *= 0.5
            
            # Если нужен комфорт - фокус на знакомых жанрах
            if context.get('mood') == 'comfort':
                if any(g in material.genre for g in user.favorite_genres):
                    result['score'] *= 1.2
        
        scored_materials.append((material, result))
    
    # Сортируем по оценке
    scored_materials.sort(key=lambda x: x[1]['score'], reverse=True)
    
    return scored_materials[:n]


# ============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Создаём примерного пользователя
    user = User(
        id="user_001",
        complexity_tolerance=6,
        meta_awareness_level=5,
        tolerance_for_deconstruction=4,
        needs_reconstruction=6,
        trope_fatigue=["chosen_one"],
        trope_interest=["unreliable_narrator"],
        enjoys_meta=False,
        genre_literacy={"sci_fi": 7, "drama": 5, "horror": 3},
        favorite_genres=["sci_fi", "drama"],
        disliked_genres=["horror"]
    )
    
    # Создаём пример материала
    material = Material(
        id="inception_2010",
        title="Inception",
        type="film",
        year=2010,
        creator=["Christopher Nolan"],
        genre=["sci_fi", "thriller"],
        complexity=7,
        transformation_score=7,
        emotional_intensity=6,
        meta_awareness=6,
        intertextual_knowledge=3,
        requires_genre_literacy=5,
        analyzed_tropes=[
            TropeAnalysis(
                trope_id="dream_within_dream",
                usage_type=TropeUsageType.STRAIGHT,
                execution=9,
                transformation_potential=8,
                requires_literacy=2
            ),
            TropeAnalysis(
                trope_id="unreliable_narrator",
                usage_type=TropeUsageType.SUBVERSION,
                execution=8,
                transformation_potential=7,
                requires_literacy=5
            )
        ],
        transformation_mechanisms=[
            "cognitive_reframe",
            "perspective_shift"
        ]
    )
    
    # Вычисляем рекомендацию
    result = calculate_recommendation_score(material, user)
    
    print("=" * 70)
    print("ОЦЕНКА РЕКОМЕНДАЦИИ")
    print("=" * 70)
    print(f"Материал: {material.title}")
    print(f"Пользователь: {user.id}")
    print(f"\nИтоговая оценка: {result['score']}/10")
    print(f"\nРазбивка:")
    print(f"  Контент: {result['breakdown']['content']}/10")
    print(f"  Структура: {result['breakdown']['structure']}/10")
    print(f"  Работа с тропами: {result['breakdown']['trope_work']}/10")
    print(f"  Трансформация: {result['breakdown']['transformation']}/10")
    
    print(f"\nЗона развития: {result['zpd_info']['challenge_level']}")
    print(f"Рекомендация: {result['zpd_info']['recommendation']}")
    
    if result['trope_details']:
        print(f"\nДетали работы с тропами:")
        for detail in result['trope_details']:
            print(f"  - {detail}")
    
    print("=" * 70)
