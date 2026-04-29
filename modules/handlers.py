import logging
import asyncio  # Додаємо імпорт
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from modules.rag import search_in_knowledge_base, format_answer_from_kb
from modules.web_search import search_web
from modules.gemini_client import summarize_with_gemini

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відповідь на команду /start"""
    welcome_text = (
        "🤖 *Вітаю у WikiBot!*\n\n"
        "Я бот з власною базою знань. Ти можеш питати мене про предмети, які додані до моєї вікі. "
        "Якщо я не знайду відповіді в базі, то пошукаю в інтернеті та стисло перекажу.\n\n"
        "📌 *Приклади:*\n"
        "• Що таке Python?\n"
        "• Поясни RAG\n"
        "• Функція calling\n\n"
        "💡 *Команди:*\n"
        "/start – це повідомлення\n"
        "/help – допомога\n"
        "/reset – очистити контекст (якщо буде додано пам'ять)"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відповідь на /help"""
    help_text = (
        "📖 *Як користуватися WikiBot:*\n\n"
        "Просто напиши мені питання про будь-який предмет або поняття. "
        "Я спочатку перевірю свою власну базу знань (JSON). Якщо не знайду – "
        "виконаю пошук в інтернеті, а ШІ стисне відповідь до 3-4 речень.\n\n"
        "Я відповідаю тільки українською та максимально коротко."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скидання (поки що заглушка, бо пам'яті немає)"""
    await update.message.reply_text("🔄 Контекст очищено (я і так не пам'ятаю історію).")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головна логіка обробки текстового повідомлення:
    1. Пошук у базі знань (RAG)
    2. Якщо знайдено – відповідь з JSON
    3. Якщо ні – пошук в інтернеті → Gemini → відповідь
    """
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Користувач {user_id}: {user_text}")

    # Показуємо, що бот "друкує"
    await update.message.chat.send_action(action=ChatAction.TYPING)

    # --- Етап 1: RAG пошук у власній JSON базі ---
    kb_result = search_in_knowledge_base(user_text)
    if kb_result:
        answer = format_answer_from_kb(kb_result)
        await update.message.reply_text(answer, parse_mode="Markdown")
        logger.info(f"Відповідь з бази знань: {kb_result['назва']}")
        return

    # --- Етап 2: Якщо не знайдено → пошук в інтернеті + Gemini ---
    logger.info(f"Предмет не знайдено в базі, шукаю в інтернеті: {user_text}")
    await update.message.reply_text("🔍 Шукаю в інтернеті та готую стислу відповідь...")
    await update.message.chat.send_action(action=ChatAction.TYPING)

    # Додаємо невелику затримку перед пошуком (щоб уникнути RateLimit)
    await asyncio.sleep(1)

    # Пошук в інтернеті
    search_results = search_web(user_text, max_results=2)  # Зменшуємо кількість результатів

    if not search_results:
        search_results = ""
        logger.info("Інтернет не дав результатів, пробуємо Gemini без контексту")

    # Стиснення через Gemini
    summary = summarize_with_gemini(user_text, search_results)

    # Додаємо позначку про джерело відповіді
    if search_results:
        prefix = "🌐 *Результат пошуку:*\n"
    else:
        prefix = "🤖 *Відповідь ШІ (без результатів пошуку):*\n"

    await update.message.reply_text(f"{prefix}{summary}", parse_mode="Markdown")