import json
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

try:
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = json.load(f)
    logger.info(f"База знань завантажена: {KNOWLEDGE_BASE['metadata']['кількість_сутностей']} сутностей")
except Exception as e:
    logger.error(f"Не вдалося завантажити knowledge_base.json: {e}")
    KNOWLEDGE_BASE = {"сутності": []}


def search_in_knowledge_base(query: str):
    """
    Шукає предмет у базі знань, оцінюючи релевантність.
    Повертає найкращий збіг або None.
    """
    query_lower = query.lower().strip()
    best_score = 0
    best_item = None

    for item in KNOWLEDGE_BASE.get("сутності", []):
        score = 0
        name = item["назва"].lower()
        keywords = [kw.lower() for kw in item.get("ключові_слова", [])]

        # 1. Точний збіг назви (найвищий пріоритет)
        if query_lower == name:
            return item

        # 2. Повна назва є частиною запиту (або навпаки)
        if name in query_lower or query_lower in name:
            score += 30

        # 3. Схожість назви (нечіткий пошук) – допомагає при одруківках
        similarity = SequenceMatcher(None, query_lower, name).ratio()
        score += similarity * 20  # максимум 20 балів

        # 4. Збіги ключових слів (кожне слово – 5 балів)
        for kw in keywords:
            if kw in query_lower:
                score += 5

        # 5. Спеціальний бонус, якщо запит містить частину унікального ідентифікатора (напр., "драугра")
        # Дивимося на ключові слова, що не є загальними ("лук", "шолом" тощо)
        stop_words = {"лук", "шолом", "броня", "меч", "сокира", "ніж", "молот", "булава", "інструмент"}
        for kw in keywords:
            if kw in query_lower and kw not in stop_words:
                score += 10  # бонус за унікальне ключове слово

        if score > best_score:
            best_score = score
            best_item = item

    # Повертаємо найкращий збіг, тільки якщо оцінка досить висока (можна підлаштувати поріг)
    if best_item and best_score >= 10:
        return best_item
    return None


def format_answer_from_kb(item: dict) -> str:
    """Форматує відповідь із бази знань."""
    name = item.get("назва", "Невідомий предмет")
    category = item.get("категорія", "")
    definition = item.get("визначення", "")
    short = item.get("коротко", "")
    characteristics = item.get("характеристики", "")

    result = f"🎯 **{name}**"
    if category:
        result += f" ({category})"
    result += f"\n\n📖 {definition}"
    if short:
        result += f"\n\n💡 {short}"
    if characteristics:
        result += f"\n\n📊 Характеристики: {characteristics}"
    return result