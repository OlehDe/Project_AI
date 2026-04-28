import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from modules.rag import search_in_knowledge_base, format_answer_from_kb
from modules.web_search import search_web
from modules.gemini_client import summarize_with_gemini

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "/reset – очистити контекст"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Як користуватися WikiBot:*\n\n"
        "Просто напиши мені питання про будь-який предмет або поняття. "
        "Я спочатку перевірю свою власну базу знань (JSON). Якщо не знайду – "
        "виконаю пошук в інтернеті, а ШІ стисне відповідь до 3-4 речень.\n\n"
        "Я відповідаю тільки українською та максимально коротко."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Контекст очищено (я і так не пам'ятаю історію).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    user_id = update.effective_user.id
    logger.info(f"Користувач {user_id}: {user_text}")

    # Перевірка на порожнє повідомлення
    if len(user_text) == 0:
        await update.message.reply_text("Будь ласка, напишіть текстове питання.")
        return

    # Обмеження довжини
    if len(user_text) > 1000:
        await update.message.reply_text("Ваше питання занадто довге (максимум 1000 символів). Спробуйте коротше.")
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)

    # RAG пошук у базі знань
    kb_result = search_in_knowledge_base(user_text)
    if kb_result:
        answer = format_answer_from_kb(kb_result)
        await update.message.reply_text(answer, parse_mode="Markdown")
        return

    # Пошук в інтернеті
    status_msg = await update.message.reply_text("🔍 Шукаю в інтернеті...")
    await update.message.chat.send_action(action=ChatAction.TYPING)

    search_results = await search_web(user_text, max_results=3)
    logger.info(f"Отримано search_results довжиною: {len(search_results) if search_results else 0} символів")

    if not search_results or len(search_results.strip()) == 0:
        await status_msg.edit_text("Не вдалося знайти інформацію в інтернеті. Спробуйте інше формулювання.")
        return

    await status_msg.edit_text("🤖 Аналізую та стискаю відповідь...")
    await update.message.chat.send_action(action=ChatAction.TYPING)

    try:
        summary = summarize_with_gemini(user_text, search_results)
        logger.info(f"Отримано відповідь від Gemini: {summary[:100]}...")
        await update.message.reply_text(f"🌐 *Результат пошуку:*\n{summary}", parse_mode="Markdown")
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Помилка при виклику summarize_with_gemini: {e}")
        await status_msg.edit_text("Вибачте, сталася помилка при обробці відповіді. Спробуйте пізніше.")