from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from server.core.config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """COnnect to MongoDB"""
    db.client = AsyncIOMotorClient(settings.MONGO_DB_URI)
    db.database = db.client["ufc-prediction"]

    await db.client.admin.command('ping')
    print(f"Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database