from pymongo import MongoClient
from datetime import datetime
from config.config import Config

class MongoDBManager:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URL)
        self.db = self.client.telegram_bot
        self.users = self.db.users
        self.users.create_index("user_id", unique=True)
    
    def add_user(self, user_id, username, first_name, last_name):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "last_active": datetime.now()
            }},
            upsert=True
        )
    
    def get_stats(self):
        return {'total': self.users.count_documents({})}

db = MongoDBManager()
