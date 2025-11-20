from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    # Start Flask server
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Self-pinging to prevent sleep
    def ping_self():
        while True:
            try:
                webhook_url = os.getenv('WEBHOOK_URL')
                if webhook_url:
                    requests.get(webhook_url)
                time.sleep(300)  # Ping every 5 minutes
            except:
                pass
    
    ping_thread = Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()
EOF# Create handlers directory
cat > handlers/__init__.py << 'EOF'
