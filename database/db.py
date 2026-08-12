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
    links_col = db["links"]
else:
    users_col = None
    banned_col = None
    settings_col = None
    links_col = None


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
            try:
                await users_col.create_index([("id", pymongo.ASCENDING)], unique=True)
            except (pymongo.errors.DuplicateKeyError, pymongo.errors.OperationFailure) as e:
                logging.getLogger(__name__).warning(f"Could not create unique index on users_col: {e}. Skipping to allow bot to start.")
        if banned_col is not None:
            try:
                await banned_col.create_index([("id", pymongo.ASCENDING)], unique=True)
            except (pymongo.errors.DuplicateKeyError, pymongo.errors.OperationFailure) as e:
                logging.getLogger(__name__).warning(f"Could not create unique index on banned_col: {e}. Skipping to allow bot to start.")
        if settings_col is not None:
            try:
                await settings_col.create_index([("id", pymongo.ASCENDING)], unique=True)
            except (pymongo.errors.DuplicateKeyError, pymongo.errors.OperationFailure) as e:
                logging.getLogger(__name__).warning(f"Could not create unique index on settings_col: {e}. Skipping to allow bot to start.")
        logging.getLogger(__name__).info("Database indexes checked/created")
    except Exception as e:
        logging.getLogger(__name__).error(f"Gagal auth: {e}")
        raise e


# Note: This cache is per-process. For multi-process deployment (like Gunicorn with multiple workers),
# you would need Redis or similar to sync cache invalidations.
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

    try:
        setting = await settings_col.find_one_and_update(
            {"id": 1},
            {"$setOnInsert": {
                "id": 1,
                "start_msg": START_MSG,
                "force_msg": FORCE_MSG,
                "auto_delete_time": 0,
                "force_sub_channels": []
            }},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        _settings_cache = setting
        return setting
    except pymongo.errors.DuplicateKeyError:
        setting = await settings_col.find_one({"id": 1})
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
            {"$set": {"username": username, "last_seen": datetime.datetime.now(datetime.timezone.utc)}},
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
    if banned_col is None:
        return False
    banned = await banned_col.find_one({"id": user_id})
    return True if banned else False


async def ban_user(user_id):
    if banned_col is None:
        return
    await banned_col.update_one({"id": user_id}, {"$set": {"id": user_id}}, upsert=True)


async def unban_user(user_id):
    if banned_col is None:
        return 0
    res = await banned_col.delete_one({"id": user_id})
    return res.deleted_count

async def save_link(token, message_ids):
    if links_col is not None:
        await links_col.update_one(
            {"token": token},
            {"$set": {"message_ids": message_ids}},
            upsert=True
        )

async def get_link(token):
    if links_col is None:
        return None
    link = await links_col.find_one({"token": token})
    return link.get("message_ids") if link else None
