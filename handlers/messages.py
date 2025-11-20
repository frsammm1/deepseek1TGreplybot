from telegram import Update
from telegram.ext import ContextTypes
from models.mongodb_manager import db
from config.config import Config

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    await update.message.reply_text("✅ Message forwarded to owner!")
    
    # Forward to owner
    await forward_to_owner(update, context)

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message
    
    try:
        user_info = f"�� From: {user.first_name} (ID: {user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(Config.OWNER_ID, user_info)
        
        if message.text:
            await context.bot.send_message(Config.OWNER_ID, f"📩 {message.text}")
        elif message.photo:
            await context.bot.send_photo(Config.OWNER_ID, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            await context.bot.send_video(Config.OWNER_ID, message.video.file_id, caption=message.caption)
        elif message.document:
            await context.bot.send_document(Config.OWNER_ID, message.document.file_id, caption=message.caption)
            
    except Exception as e:
        print(f"Forward error: {e}")

async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message.reply_to_message and 
        update.effective_user.id == Config.OWNER_ID):
        
        replied_msg = update.message.reply_to_message.text
        if "👤 From:" in replied_msg:
            try:
                lines = replied_msg.split('\n')
                id_line = [l for l in lines if "ID:" in l][0]
                user_id = int(id_line.split('ID: ')[1].split(')')[0]
                
                if update.message.text:
                    await context.bot.send_message(user_id, f"💌 From owner:\n{update.message.text}")
                
                await update.message.reply_text("✅ Reply sent!")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
