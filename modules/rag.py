import json
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

try:
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = json.load(f)
    # Виправлено: використовуємо правильний ключ "сутності" та "кількість_сутностей"
    count = len(KNOWLEDGE_BASE.get("сутності", []))
    logger.info(f"База знань завантажена: {count} сутностей")
except Exception as e:
    logger.error(f"Не вдалося завантажити knowledge_base.json: {e}")
    KNOWLEDGE_BASE = {"сутності": []}  # Виправлено ключ за замовчуванням


def search_in_knowledge_base(query: str):
    """
    Шукає предмет у базі знань, оцінюючи релевантність.
    Повертає найкращий збіг або None.
    """
    query_lower = query.lower().strip()
    best_score = 0
    best_item = None

    # Виправлено: використовуємо "сутності" замість "предмети"
    for item in KNOWLEDGE_BASE.get("сутності", []):
        score = 0
        name = item["назва"].lower()
        keywords = [kw.lower() for kw in item.get("ключові_слова", [])]

        # 1. Точний збіг назви (найвищий пріоритет)
        if query_lower == name:
            logger.info(f"Точний збіг: {item['назва']}")
            return item

        # 2. Повна назва є частиною запиту
        if name in query_lower:
            score += 35
            logger.debug(f"Назва '{name}' є частиною запиту '{query_lower}', +35")

        # 3. Запит є частиною назви
        if query_lower in name:
            score += 25
            logger.debug(f"Запит '{query_lower}' є частиною назви '{name}', +25")

        # 4. Схожість назви для нечіткого пошуку
        similarity = SequenceMatcher(None, query_lower, name).ratio()
        score += similarity * 20
        if similarity > 0.5:
            logger.debug(f"Схожість '{query_lower}' з '{name}': {similarity:.2f}, +{similarity * 20:.1f}")

        # 5. Збіги ключових слів (кожне слово — 5 балів)
        for kw in keywords:
            if kw in query_lower:
                score += 5
                logger.debug(f"Ключове слово '{kw}' знайдено в запиті, +5")

        # 6. Бонус за унікальні ключові слова
        common_words = {"лук", "шолом", "броня", "меч", "сокира", "ніж", "молот", "булава", "інструмент",
                       "штани", "плащ", "нагрудник", "туніка", "каптур", "обладунок"}
        for kw in keywords:
            if kw in query_lower and kw not in common_words:
                score += 10
                logger.debug(f"Унікальне ключове слово '{kw}' знайдено, +10")

        if score > best_score:
            best_score = score
            best_item = item

    # Повертаємо найкращий збіг, якщо оцінка достатньо висока
    if best_item and best_score >= 5:  # Знижено поріг для кращого пошуку
        logger.info(f"Знайдено: {best_item['назва']} (score: {best_score})")
        return best_item

    logger.info(f"Нічого не знайдено. Найкраща оцінка: {best_score}")
    return None


def format_answer_from_kb(item: dict) -> str:
    """Форматує відповідь з бази знань"""
    name = item.get("назва", "Невідомий предмет")
    category = item.get("категорія", "")
    definition = item.get("визначення", "")
    short = item.get("коротко", "")
    example = item.get("приклад", "")
    characteristics = item.get("характеристики", "")

    result = f"📚 *{name}*"
    if category:
        result += f" ({category})"

    result += f"\n\n📖 {definition}"

    if short:
        result += f"\n\n💡 {short}"

    if example:
        result += f"\n\n📌 Приклад: {example}"

    if characteristics:
        result += f"\n\n📊 Характеристики: {characteristics}"

    return result