import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

# Отримуємо API ключ зі змінних середовища
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не знайдено в .env")

# Ініціалізуємо клієнта
client = genai.Client(api_key=GEMINI_API_KEY)

# СИСТЕМНИЙ ПРОМПТ (керує поведінкою моделі для стиснення)
SYSTEM_PROMPT = """Ти — WikiBot, стислий та точний ШІ-асистент.

## ТВОЯ РОЛЬ
Ти допомагаєш користувачам отримувати короткі, зрозумілі відповіді на їхні питання.

## ВАЖЛИВІ ПРАВИЛА (НЕ ПОРУШУЙ!)

1. ВІДПОВІДАЙ ТІЛЬКИ НА УКРАЇНСЬКІЙ МОВІ.
2. МАКСИМУМ 3-4 РЕЧЕННЯ НА ВІДПОВІДЬ — НІЯКОЇ "ВОДИ"!
3. ЯКЩО НЕ ЗНАЄШ ТОЧНОЇ ВІДПОВІДІ — СКАЖИ ЧЕСНО, ЩО НЕ ЗНАЄШ — НЕ ВИГАДУЙ!
4. НЕ ДОДАВАЙ ВІТАННЯ, ПРОЩАННЯ, ЕМОДЗІ ТА ЗАЙВІ СЛОВА.
5. ВИКОРИСТОВУЙ ПРОСТУ, ЗРОЗУМІЛУ ДЛЯ ПОЧАТКІВЦЯ МОВУ.

## ФОРМАТ ВІДПОВІДІ
Відповідай ТІЛЬКИ текстом у такому стилі:
[Одна стисла відповідь на питання без зайвих конструкцій]

## ВАЖЛИВО ПРО ДЖЕРЕЛА
- Якщо є результати пошуку — використовуй тільки їх
- Якщо результатів пошуку немає — дай відповідь на основі своїх знань
- Якщо не впевнений у відповіді — так і скажи

## ПРИКЛАДИ

Питання: "Що таке Python?"
Відповідь: Python — це мова програмування, яку легко вивчати. Вона широко використовується для штучного інтелекту, аналізу даних та веб-розробки.

Питання: "Хто такий Ілон Маск?"
Відповідь: Ілон Маск — американський підприємець, засновник SpaceX та Tesla. Відомий своїми інноваціями в космічній галузі та електромобілях.
"""


def summarize_with_gemini(question: str, search_results: str) -> str:
    """
    Надсилає питання та результати пошуку до Gemini з системним промптом,
    отримує стислу відповідь.
    """
    # Формуємо користувацький промпт з даними
    if search_results and len(search_results.strip()) > 0:
        user_content = f"""
<user_question>
{question}
</user_question>

<search_results>
{search_results}
</search_results>

ІНСТРУКЦІЯ: Використовуючи результати пошуку, дай стислу відповідь (3-4 речення) українською мовою.
"""
    else:
        # Якщо немає результатів пошуку, просимо Gemini відповісти з власних знань
        user_content = f"""
<user_question>
{question}
</user_question>

<search_results>
Результати пошуку в інтернеті відсутні.
</search_results>

ІНСТРУКЦІЯ: Результатів пошуку немає. Дай стислу відповідь (3-4 речення) українською мовою на основі своїх знань. Якщо не знаєш точної відповіді — чесно скажи про це.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=300
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Помилка Gemini API: {e}")
        return "Вибачте, сталася технічна помилка при зверненні до ШІ. Спробуйте пізніше."