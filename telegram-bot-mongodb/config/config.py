import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    OWNER_ID = int(os.getenv('OWNER_ID', 0))
    MONGODB_URL = os.getenv('MONGODB_URL')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    PORT = int(os.getenv('PORT', 10000))
    
    PREMIUM_PRICES = {'1': 5, '7': 25, '30': 80}
EOF# Create MongoDB manager
cat > models/__init__.py << 'EOF'
