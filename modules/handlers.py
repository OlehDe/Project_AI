import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from modules.rag import search_in_knowledge_base_multi, format_answer_from_kb
from modules.gemini_client import ask_gemini_valheim

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 *Вітаю у Valheim AI!*\n\n"
        "Я твій персональний помічник з гри Valheim. Запитай мене про що завгодно: "
        "поради, предмети, босів, білди — і я відповім стисло та зрозуміло.\n\n"
        "💡 Просто пиши, як другу."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Як користуватися Valheim WikiBot:*\n\n"
        "Постав будь-яке запитання про гру Valheim. "
        "Я відповім українською та максимально коротко."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Контекст очищено (я не пам'ятаю історію).")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Користувач {user_id}: {user_text}")

    await update.message.chat.send_action(action=ChatAction.TYPING)

    # 1. Шукаємо в базі знань
    relevant_items = search_in_knowledge_base_multi(user_text)
    context_text = ""
    if relevant_items:
        parts = []
        for item in relevant_items:
            parts.append(
                f"Назва: {item['назва']}\n"
                f"Опис: {item.get('коротко', '')}\n"
                f"Характеристики: {item.get('характеристики', '')}"
            )
        context_text = "\n---\n".join(parts)
        logger.info(f"Знайдено {len(relevant_items)} предметів для контексту")

    # 2. Питаємо Gemini
    answer = ask_gemini_valheim(user_text, context_text)

    # 3. Якщо Gemini не відповів — показуємо з бази
    if answer == "ERROR_API":
        if relevant_items:
            answer = format_answer_from_kb(relevant_items[0])
            answer = f"⚠️ *ШІ тимчасово недоступний. Дані з бази знань:*\n\n{answer}"
        else:
            answer = "🤷 Не знайшов інформації ні в базі, ні через ШІ. Спробуй перефразувати."

    await update.message.reply_text(answer, parse_mode="Markdown")