from flask import Flask
import threading
from bot import main

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK"

# Start bot in background
def start_bot():
    try:
        main()
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == '__main__':
    # Start bot in separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask server
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
