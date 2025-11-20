import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config.config import Config
from handlers.commands import start, admin, premium_info, handle_callback, setup_bot, handle_bot_token, cancel, AWAITING_BOT_TOKEN
from handlers.messages import handle_message, handle_owner_reply, forward_to_owner
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
