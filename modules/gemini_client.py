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

SYSTEM_PROMPT = """Ти — дружній помічник з гри Valheim. Ти глибоко знаєш гру: предмети, рецепти, біоми, босів, тактики, секрети.
Відповідай українською мовою.

## ПРАВИЛА
1. Відповідай тільки українською.
2. Будь стислим (3-4 речення), але доброзичливим.
3. Якщо тобі надали інформацію з бази знань, обов'язково використай її у відповіді.
4. Якщо питання не про Valheim — ввічливо скажи, що ти розмовляєш лише на теми Valheim.
"""

def ask_gemini_valheim(question: str, context: str = "") -> str:
    """
    Задає питання Gemini у ролі Valheim-експерта.
    context — додаткова інформація з бази знань (може бути порожнім).
    """
    if context:
        user_content = f"""Інформація з бази знань:
{context}

Запитання гравця:
{question}

Дай стислу, корисну відповідь українською, використовуючи цю інформацію.
"""
    else:
        user_content = f"""Запитання гравця:
{question}

Дай стислу, корисну відповідь українською (3-4 речення). Якщо питання не про Valheim, ввічливо відмов.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # ✅ Найкраща безкоштовна модель
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.5,
                max_output_tokens=300,
            ),
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Помилка Gemini API: {e}")
        # Повертаємо зрозуміле повідомлення замість вильоту
        return "На жаль, сталася помилка при зверненні до ШІ. Спробуй ще раз."