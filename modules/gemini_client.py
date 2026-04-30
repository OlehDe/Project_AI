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

SYSTEM_PROMPT = """Ти – персональний помічник з гри Valheim. Ти добре знаєш усі аспекти гри. Спілкуйся українською мовою, доброзичливо, але коротко (3-4 речення).

Якщо тобі дано додаткову інформацію з бази знань, використай її, щоб дати корисну пораду, але НЕ перераховуй всі характеристики сухим списком. Відповідай так, ніби пояснюєш другу.

Якщо питання не стосується Valheim, ввічливо відмов.
"""


def ask_gemini_valheim(question: str, context: str = "") -> str:
    """
    Запитує Gemini з автоматичним перемиканням між моделями.
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

    # Моделі в порядку пріоритету
    models = ["gemini-2.5-flash", "gemini-2.0-flash"]

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.5,
                    max_output_tokens=300,
                ),
            )
            logger.info(f"Успішно використано модель: {model_name}")
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Модель {model_name} недоступна: {e}")
            continue

    # Якщо жодна модель не спрацювала
    logger.error("Жодна модель Gemini не доступна")
    return "ERROR_API"