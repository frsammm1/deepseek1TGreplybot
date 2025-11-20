from telegram import Update
from telegram.ext import ContextTypes
from models.mongodb_manager import db
from config.config import Config

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
    await update.message.reply_text(f"📊 Users: {stats['total']}")
