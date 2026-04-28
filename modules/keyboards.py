from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    buttons = [
        [KeyboardButton("📖 Допомога"), KeyboardButton("🔄 Очистити")],
        [KeyboardButton("❓ Що ти вмієш?")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)