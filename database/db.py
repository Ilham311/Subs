import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, START_MSG, FORCE_MSG

# Connect to MongoDB
import logging

import urllib.parse

try:
    client = AsyncIOMotorClient(DB_URI, serverSelectionTimeoutMS=5000)
    parsed_uri = urllib.parse.urlparse(DB_URI)
    db_name = parsed_uri.path.lstrip('/') if parsed_uri.path != '/' and parsed_uri.path else "force_subs_bot"
    db = client[db_name]
except Exception as e:
    logging.getLogger(__name__).error(f"Failed to connect to MongoDB: {e}")
    db = None
    client = None

# Collections
if db is not None:
    users_col = db["users"]
    banned_col = db["banned"]
    settings_col = db["settings"]
else:
    users_col = None
    banned_col = None
    settings_col = None


import pymongo

async def ensure_connection():
    if client is None:
        logging.getLogger(__name__).error("Gagal auth: Motor client tidak diinisialisasi karena error sebelumnya.")
        raise Exception("Gagal auth: Motor client tidak diinisialisasi karena error sebelumnya.")
    try:
        await client.admin.command('ping')
        logging.getLogger(__name__).info("MongoDB terhubung")

        # Create indexes
        if users_col is not None:
            await users_col.create_index([("id", pymongo.ASCENDING)], unique=True)
        if banned_col is not None:
            await banned_col.create_index([("id", pymongo.ASCENDING)], unique=True)
        logging.getLogger(__name__).info("Database indexes checked/created")
    except Exception as e:
        logging.getLogger(__name__).error(f"Gagal auth: {e}")
        raise e


# Note: This cache is per-process. For multi-process deployment (like Gunicorn with multiple workers),
# you would need Redis or similar to sync cache invalidations.
_settings_cache = None


async def invalidate_settings_cache():
    global _settings_cache
    _settings_cache = None


async def get_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache

    if db is None:
        return {
            "id": 1,
            "start_msg": START_MSG,
            "force_msg": FORCE_MSG,
            "auto_delete_time": 0,
        }

    setting = await settings_col.find_one({"id": 1})
    if not setting:
        # Create default settings
        default = {
            "id": 1,
            "start_msg": START_MSG,
            "force_msg": FORCE_MSG,
            "auto_delete_time": 0,  # 0 means disabled
            "force_sub_channels": []
        }
        await settings_col.insert_one(default)
        _settings_cache = default
        return default
    _settings_cache = setting
    return setting


async def update_settings(key, value):
    global _settings_cache
    if db is not None:
        await settings_col.update_one({"id": 1}, {"$set": {key: value}}, upsert=True)
    if _settings_cache is not None:
        _settings_cache[key] = value
    else:
        # Ensure we populate cache
        await get_settings()
        if _settings_cache is not None:
            _settings_cache[key] = value


import datetime

async def add_user(user_id, username=None):
    if users_col is not None:
        await users_col.update_one(
            {"id": user_id},
            {"$set": {"username": username, "last_seen": datetime.datetime.utcnow()}},
            upsert=True
        )


async def delete_user(user_id):
    if users_col is not None:
        await users_col.delete_one({"id": user_id})


async def get_all_users():
    if users_col is not None:
        async for user in users_col.find({}):
            yield user

async def get_all_users_count():
    if users_col is not None:
        return await users_col.count_documents({})
    return 0


async def is_banned(user_id):
    banned = await banned_col.find_one({"id": user_id})
    return True if banned else False


async def ban_user(user_id):
    await banned_col.insert_one({"id": user_id})


async def unban_user(user_id):
    await banned_col.delete_one({"id": user_id})
