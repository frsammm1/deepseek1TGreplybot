from telegram import Update
from telegram.ext import ContextTypes
from utils.greetings import get_greeting
from models.mongodb_manager import db
from config.config import Config

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # Check if banned
    user_data = db.users.find_one({"user_id": user.id})
    if user_data and user_data.get('is_banned'):
        await update.message.reply_text("❌ You are banned.")
        return
    
    # Add/update user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    # Send greeting
    await update.message.reply_text(get_greeting())
    
    # Forward to owner
    await forward_to_owner(update, context)

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message
    
    try:
        # Send user info
        user_info = f"👤 From: {user.first_name} (ID: {user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(Config.OWNER_ID, user_info)
        
        # Forward message
        if message.text:
            await context.bot.send_message(
                Config.OWNER_ID, 
                f"📩 {message.text}"
            )
        elif message.photo:
            await context.bot.send_photo(
                Config.OWNER_ID,
                message.photo[-1].file_id,
                caption=message.caption
            )
        elif message.video:
            await context.bot.send_video(
                Config.OWNER_ID,
                message.video.file_id, 
                caption=message.caption
            )
        elif message.document:
            await context.bot.send_document(
                Config.OWNER_ID,
                message.document.file_id,
                caption=message.caption
            )
            
    except Exception as e:
        print(f"Forward error: {e}")

async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message.reply_to_message and 
        update.effective_user.id == Config.OWNER_ID):
        
        replied_msg = update.message.reply_to_message.text
        if "👤 From:" in replied_msg:
            try:
                # Extract user ID
                lines = replied_msg.split('\n')
                id_line = [l for l in lines if "ID:" in l][0]
                user_id = int(id_line.split('ID: ')[1].split(')')[0])
                
                # Send reply
                if update.message.text:
                    await context.bot.send_message(
                        user_id, 
                        f"💌 From owner:\n{update.message.text}"
                    )
                elif update.message.photo:
                    await context.bot.send_photo(
                        user_id,
                        update.message.photo[-1].file_id,
                        caption=update.message.caption
                    )
                
                await update.message.reply_text("✅ Reply sent!")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
EOFcat > handlers/commands.py << 'EOF'
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.greetings import get_welcome
from utils.helpers import admin_keyboard, user_keyboard
from models.mongodb_manager import db
from config.config import Config

# States
AWAITING_BOT_TOKEN = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    text = get_welcome()
    is_owner = user.id == Config.OWNER_ID
    
    if is_owner:
        text += "\n\n👑 **Owner Access** - Use /admin"
    
    if db.is_premium(user.id):
        text += "\n⭐ **Premium User** - Use /setupbot"
        bot_data = db.get_user_bot(user.id)
        if bot_data:
            text += f"\n🤖 Your bot: @{bot_data['bot_username']}"
    
    await update.message.reply_text(
        text,
        reply_markup=user_keyboard(is_owner),
        parse_mode='Markdown'
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.OWNER_ID:
        await update.message.reply_text("❌ Owner only.")
        return
    
    stats = db.get_stats()
    text = f"""👑 **Admin Panel**

📊 Stats:
• Users: {stats['total']}
• Active: {stats['active']} 
• Banned: {stats['banned']}

Choose an option:"""
    
    await update.message.reply_text(text, reply_markup=admin_keyboard())

async def premium_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """⭐ **Get Your Own Bot!**

Features:
• Message forwarding
• All media support  
• 24/7 hosting

Pricing:
• 1 Day: $5
• 7 Days: $25
• 30 Days: $80

Contact @your_username to buy!"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def setup_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not db.is_premium(user.id) and user.id != Config.OWNER_ID:
        await update.message.reply_text("❌ Premium feature.")
        return
    
    text = """🤖 **Bot Setup**

1. Create bot with @BotFather
2. Send me the bot token
3. I'll set it up!

Format: 123456789:ABCdefGHIjklMNO...

Send token now or /cancel"""
    
    context.user_data['awaiting_token'] = True
    await update.message.reply_text(text)
    return AWAITING_BOT_TOKEN

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "stats":
        stats = db.get_stats()
        text = f"📊 Users: {stats['total']}, Active: {stats['active']}, Banned: {stats['banned']}"
        await query.edit_message_text(text)
    
    elif query.data == "premium_key":
        # Create 7-day key for example
        key = db.create_premium_key(7)
        await query.edit_message_text(f"🔑 Premium Key (7 days):\n`{key}`", parse_mode='Markdown')
    
    elif query.data == "keep_alive":
        await query.edit_message_text("🔄 Keep alive triggered!")
    
    elif query.data == "premium_info":
        await premium_info_callback(update, context)

async def premium_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = """⭐ **Get Your Own Bot!**

Contact @your_username to purchase premium!"""
    await query.edit_message_text(text, parse_mode='Markdown')

async def handle_bot_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_token'):
        return ConversationHandler.END
    
    token = update.message.text.strip()
    
    if ':' in token and token.count(':') == 1:
        # Validate token (simplified)
        try:
            # Get bot info
            from telegram import Bot
            test_bot = Bot(token=token)
            bot_user = await test_bot.get_me()
            
            # Save to database
            db.add_user_bot(update.effective_user.id, token, bot_user.username)
            
            await update.message.reply_text(
                f"✅ Bot setup complete!\n"
                f"Your bot: @{bot_user.username}\n"
                f"Users can now message your bot!"
            )
            
        except Exception as e:
            await update.message.reply_text("❌ Invalid token.")
    else:
        await update.message.reply_text("❌ Invalid token format.")
    
    context.user_data['awaiting_token'] = False
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END
EOF# Create main bot file
cat > bot.py << 'EOF'
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config.config import Config
from handlers.commands import start, admin, premium_info, setup_bot, handle_callback, handle_bot_token, cancel, AWAITING_BOT_TOKEN
from handlers.messages import handle_message, handle_owner_reply
from utils.keep_alive import start_keep_alive

# Load environment
load_dotenv()

def main():
    # Start keep-alive system
    start_keep_alive()
    
    # Create bot application
    app = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("premium", premium_info))
    
    # Bot setup conversation
    setup_handler = ConversationHandler(
        entry_points=[CommandHandler("setupbot", setup_bot)],
        states={
            AWAITING_BOT_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bot_token)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(setup_handler)
    
    # Callback queries
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.DOCUMENT, handle_message))
    
    # Owner replies
    app.add_handler(MessageHandler(filters.REPLY, handle_owner_reply))
    
    print("🤖 Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
