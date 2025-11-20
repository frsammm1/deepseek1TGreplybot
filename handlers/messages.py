from telegram import Update
from telegram.ext import ContextTypes
from models.mongodb_manager import db
from config.config import Config

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    await update.message.reply_text("✅ Message forwarded to owner!")
    
    # Forward to owner
    try:
        user_info = f"👤 From: {user.first_name} (ID: {user.id})"
        await context.bot.send_message(Config.OWNER_ID, user_info)
        
        if update.message.text:
            await context.bot.send_message(Config.OWNER_ID, f"📩 {update.message.text}")
    except Exception as e:
        print(f"Error: {e}")
