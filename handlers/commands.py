from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from models.mongodb_manager import db
from config.config import Config

# Conversation states
AWAITING_BOT_TOKEN = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    text = "🤖 Welcome! Send any message to contact owner."
    if user.id == Config.OWNER_ID:
        text += "\n👑 Owner: Use /admin"
    
    await update.message.reply_text(text)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.OWNER_ID:
        await update.message.reply_text("❌ Owner only.")
        return
    
    stats = db.get_stats()
    text = f"""👑 Admin Panel

📊 Stats:
• Total Users: {stats['total']}

Use /premium for premium features"""
    
    await update.message.reply_text(text)

async def premium_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """⭐ Premium Features

Want your own bot? Contact owner!"""
    await update.message.reply_text(text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 Feature activated!")

async def setup_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot setup - coming soon!")
    return ConversationHandler.END

async def handle_bot_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Token received!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END
