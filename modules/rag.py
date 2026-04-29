import json
import os
import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)

# Завантажуємо базу знань при старті (щоб не читати диск кожен раз)
try:
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = json.load(f)
    logger.info(f"База знань завантажена: {KNOWLEDGE_BASE['metadata']['кількість_предметів']} предметів")
except Exception as e:
    logger.error(f"Не вдалося завантажити knowledge_base.json: {e}")
    KNOWLEDGE_BASE = {"предмети": []}


def search_in_knowledge_base(query: str):
    """
    Шукає предмет у JSON базі за назвою або ключовими словами.
    Повертає словник з інформацією або None.
    """
    query_lower = query.lower()
    best_match = None
    best_score = 0

    for item in KNOWLEDGE_BASE.get("предмети", []):
        # Перевіряємо назву
        if query_lower == item["назва"].lower():
            return item
        # Частковий збіг назви
        if item["назва"].lower() in query_lower or query_lower in item["назва"].lower():
            return item
        # Перевіряємо ключові слова
        for kw in item.get("ключові_слова", []):
            if kw in query_lower:
                return item
        close = get_close_matches(query_lower, [item["назва"].lower()] + item.get("ключові_слова", []), cutoff=0.6)
        if close:
            return item

    return None


def format_answer_from_kb(item: dict) -> str:
    """Форматує відповідь з бази знань у короткий текст (3-4 речення)"""
    name = item["назва"]
    short = item["коротко"]
    definition = item["визначення"]
    example = item.get("приклад", "")
    result = f"🔍 **{name}**: {definition}\n\n{short}"
    if example:
        result += f"\n\n📌 Наприклад: {example}"
    return result