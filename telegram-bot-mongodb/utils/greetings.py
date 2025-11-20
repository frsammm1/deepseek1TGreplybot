import random

greetings = [
    "👋 Hello! Message delivered to owner!",
    "🌟 Hey! Owner will reply soon!",
    "💫 Hi! Your message is forwarded!",
    "�� Message sent successfully!",
    "🎉 Owner notified about your message!"
]

def get_greeting():
    return random.choice(greetings)

def get_welcome():
    return """
🤖 **Welcome to Message Bot!**

📩 Send any message to contact the owner
💬 Owner will reply directly to you
📁 Supports: Text, Photos, Videos, Files

⭐ Want your own bot? Contact owner!
"""
