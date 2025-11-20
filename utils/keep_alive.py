from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Running!"

def run_flask():
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    def ping_self():
        while True:
            try:
                webhook_url = os.getenv('WEBHOOK_URL')
                if webhook_url:
                    requests.get(webhook_url)
                time.sleep(300)
            except:
                pass
    
    ping_thread = Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()
