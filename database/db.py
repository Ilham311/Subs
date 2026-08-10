import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, START_MSG, FORCE_MSG

# Connect to MongoDB
import logging

import sys

try:
    client = AsyncIOMotorClient(DB_URI, serverSelectionTimeoutMS=5000)

    async def _ping():
        try:
            await client.admin.command("ping")
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Failed to ping MongoDB: {e}. Check if URL is correct, IP is whitelisted, or password is valid."
            )
            sys.exit(1)

    def _run_ping():
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            loop.create_task(_ping())
        else:
            loop.run_until_complete(_ping())

    _run_ping()

    db = client["force_subs_bot"]
except SystemExit:
    db = None
except Exception as e:
    logging.getLogger(__name__).error(
        f"Failed to connect to MongoDB: {e}. Check if URL is correct, IP is whitelisted, or password is valid."
    )
    db = None

# Collections
if db is not None:
    users_col = db["users"]
    banned_col = db["banned"]
    settings_col = db["settings"]
else:
    users_col = None
    banned_col = None
    settings_col = None


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


async def add_user(user_id, username=None):
    user = await users_col.find_one({"id": user_id})
    if not user:
        await users_col.insert_one({"id": user_id, "username": username})


async def delete_user(user_id):
    if users_col is not None:
        await users_col.delete_one({"id": user_id})


async def get_all_users():
    return await users_col.find({}).to_list(length=None)


async def is_banned(user_id):
    banned = await banned_col.find_one({"id": user_id})
    return True if banned else False


async def ban_user(user_id):
    await banned_col.insert_one({"id": user_id})


async def unban_user(user_id):
    await banned_col.delete_one({"id": user_id})
