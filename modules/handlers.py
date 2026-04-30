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
        "Я твій персональний помічник з гри Valheim. "
        "Запитай мене про що завгодно: поради, предмети, босів, білд — і я відповім стисло та зрозуміло.\n\n"
        "💡 Просто пиши, як другу."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Я знаю все про Valheim. Приклади запитань:\n"
        "• Як швидко добути залізо?\n"
        "• Який лук найкращий проти драконів?\n"
        "• Поради для новачка\n\n"
        "Просто постав запитання — я відповім."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Я не зберігаю історію, тому контекст і так порожній.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Користувач {user_id}: {user_text}")

    await update.message.chat.send_action(action=ChatAction.TYPING)

    relevant_items = search_in_knowledge_base_multi(user_text)
    if relevant_items:
        # Тимчасово виводимо перший знайдений предмет
        answer = format_answer_from_kb(relevant_items[0])
        await update.message.reply_text(answer, parse_mode="Markdown")
        return
    else:
        await update.message.reply_text(
            "🤷 Не знайшов нічого в базі знань. Спробуй перефразувати."
        )