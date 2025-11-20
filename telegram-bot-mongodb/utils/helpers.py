from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("�� Stats", callback_data="stats")],
        [InlineKeyboardButton("👥 Users", callback_data="users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🔑 Premium Key", callback_data="premium_key")],
        [InlineKeyboardButton("🔄 Keep Alive", callback_data="keep_alive")]
    ])

def user_keyboard(is_owner=False):
    keyboard = []
    if not is_owner:
        keyboard.append([InlineKeyboardButton(
            "⭐ Get Your Bot", callback_data="premium_info"
        )])
    keyboard.append([InlineKeyboardButton("📞 Contact", url="https://t.me/your_username")])
    return InlineKeyboardMarkup(keyboard)
