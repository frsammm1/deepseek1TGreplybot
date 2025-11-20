from pymongo import MongoClient
from datetime import datetime, timedelta
import secrets
from config.config import Config

class MongoDBManager:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URL)
        self.db = self.client.telegram_bot
        self._setup_collections()
    
    def _setup_collections(self):
        self.users = self.db.users
        self.premium_keys = self.db.premium_keys
        self.premium_users = self.db.premium_users
        self.user_bots = self.db.user_bots
        
        # Create indexes
        self.users.create_index("user_id", unique=True)
        self.premium_keys.create_index("auth_key", unique=True)
        self.premium_users.create_index("user_id", unique=True)
        self.user_bots.create_index("user_id", unique=True)
    
    def add_user(self, user_id, username, first_name, last_name):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "username": username,
                "first_name": first_name, 
                "last_name": last_name,
                "is_active": True,
                "is_banned": False,
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }},
            upsert=True
        )
    
    def update_activity(self, user_id):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.now()}}
        )
    
    def get_stats(self):
        return {
            'total': self.users.count_documents({}),
            'active': self.users.count_documents({"is_active": True, "is_banned": False}),
            'banned': self.users.count_documents({"is_banned": True})
        }
    
    def get_users(self):
        return list(self.users.find().sort("last_active", -1))
    
    def create_premium_key(self, days):
        auth_key = f"PREMIUM_{secrets.token_hex(6).upper()}"
        self.premium_keys.insert_one({
            "auth_key": auth_key,
            "days": days,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=days),
            "is_used": False,
            "is_revoked": False
        })
        return auth_key
    
    def validate_premium_key(self, auth_key, user_id):
        key = self.premium_keys.find_one({
            "auth_key": auth_key, 
            "is_used": False, 
            "is_revoked": False
        })
        
        if key and key['expires_at'] > datetime.now():
            # Mark key used
            self.premium_keys.update_one(
                {"auth_key": auth_key},
                {"$set": {"is_used": True, "used_by": user_id}}
            )
            # Add premium user
            self.premium_users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "auth_key": auth_key,
                    "subscribed_at": datetime.now(),
                    "expires_at": key['expires_at'],
                    "is_active": True
                }},
                upsert=True
            )
            return True
        return False
    
    def is_premium(self, user_id):
        user = self.premium_users.find_one({
            "user_id": user_id,
            "is_active": True,
            "expires_at": {"$gt": datetime.now()}
        })
        return user is not None
    
    def add_user_bot(self, user_id, bot_token, bot_username):
        self.user_bots.update_one(
            {"user_id": user_id},
            {"$set": {
                "bot_token": bot_token,
                "bot_username": bot_username,
                "created_at": datetime.now(),
                "is_active": True
            }},
            upsert=True
        )
    
    def get_user_bot(self, user_id):
        return self.user_bots.find_one({"user_id": user_id})
    
    def ban_user(self, user_id):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )

# Global instance
db = MongoDBManager()
EOF# Create utilities
cat > utils/__init__.py << 'EOF'
