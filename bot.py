import os
import logging
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from modules.handlers import start, help_command, reset, handle_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не знайдено в .env")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("WikiBot запущено...")
    app.run_polling()


if __name__ == "__main__":
    main()