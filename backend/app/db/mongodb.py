from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database():
    return client[settings.MONGODB_DB_NAME]


# Collection accessors
def get_users_collection():
    return get_database()["users"]

def get_cancer_results_collection():
    return get_database()["cancer_results"]

def get_chat_history_collection():
    return get_database()["chat_history"]

def get_period_logs_collection():
    return get_database()["period_logs"]
