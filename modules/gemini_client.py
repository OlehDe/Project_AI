import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не знайдено в .env")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ти — WikiBot, стислий та точний ШІ-асистент.

## ТВОЯ РОЛЬ
Ти допомагаєш користувачам отримувати короткі, зрозумілі відповіді на їхні питання.

## ВАЖЛИВІ ПРАВИЛА (НЕ ПОРУШУЙ!)

1. ВІДПОВІДАЙ ТІЛЬКИ НА УКРАЇНСЬКІЙ МОВІ.
2. МАКСИМУМ 3-4 РЕЧЕННЯ НА ВІДПОВІДЬ — НІЯКОЇ "ВОДИ"!
3. ЯКЩО НЕ ЗНАЄШ ТОЧНОЇ ВІДПОВІДІ — СКАЖИ "Не знайшов точної інформації" — НЕ ВИГАДУЙ!
4. НЕ ДОДАВАЙ ВІТАННЯ, ПРОЩАННЯ, ЕМОДЗІ ТА ЗАЙВІ СЛОВА.
5. ВИКОРИСТОВУЙ ПРОСТУ, ЗРОЗУМІЛУ ДЛЯ ПОЧАТКІВЦЯ МОВУ.

## ФОРМАТ ВІДПОВІДІ
Відповідай ТІЛЬКИ текстом у такому стилі:
[Одна стисла відповідь на питання без зайвих конструкцій]
"""

def summarize_with_gemini(question: str, search_results: str) -> str:
    if not search_results or not isinstance(search_results, str) or len(search_results.strip()) == 0:
        return "Не знайшов точної інформації в інтернеті. Спробуйте переформулювати питання."

    # Обрізаємо результати пошуку, щоб не перевищити ліміт токенів
    truncated_results = search_results[:3000] if len(search_results) > 3000 else search_results

    user_content = f"""
<user_question>
{question}
</user_question>

<search_results>
{truncated_results}
</search_results>

ІНСТРУКЦІЯ: На основі виключно результатів пошуку дай стислу відповідь (3-4 речення) українською мовою.
"""
    try:
        logger.info("Надсилаю запит до Gemini API...")
        response = client.models.generate_content(
            model="gemma-3-2b",  # або gemini-1.5-flash
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=300
            )
        )
        if response.text:
            logger.info("Отримано відповідь від Gemini")
            return response.text.strip()
        else:
            logger.error("Gemini повернув порожню відповідь")
            return "Не вдалося отримати відповідь від ШІ."
    except Exception as e:
        logger.error(f"Помилка Gemini API: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return "Вибачте, сталася технічна помилка при зверненні до ШІ. Спробуйте пізніше."