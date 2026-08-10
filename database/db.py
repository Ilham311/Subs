import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, START_MSG, FORCE_MSG

# Connect to MongoDB
client = AsyncIOMotorClient(DB_URI)
db = client['force_subs_bot']

# Collections
users_col = db['users']
banned_col = db['banned']
settings_col = db['settings']
fsubs_col = db['fsubs']

async def get_settings():
    setting = await settings_col.find_one({"id": 1})
    if not setting:
        # Create default settings
        default = {
            "id": 1,
            "start_msg": START_MSG,
            "force_msg": FORCE_MSG,
            "auto_delete_time": 0 # 0 means disabled
        }
        await settings_col.insert_one(default)
        return default
    return setting

async def update_settings(key, value):
    await settings_col.update_one({"id": 1}, {"$set": {key: value}}, upsert=True)

async def add_user(user_id, username=None):
    user = await users_col.find_one({"id": user_id})
    if not user:
        await users_col.insert_one({"id": user_id, "username": username})

async def get_all_users():
    return await users_col.find({}).to_list(length=None)

async def is_banned(user_id):
    banned = await banned_col.find_one({"id": user_id})
    return True if banned else False

async def ban_user(user_id):
    await banned_col.insert_one({"id": user_id})

async def unban_user(user_id):
    await banned_col.delete_one({"id": user_id})

async def get_fsubs():
    return await fsubs_col.find({}).to_list(length=None)

async def add_fsub(chat_id, invite_link=None, title=None):
    fsub = await fsubs_col.find_one({"chat_id": chat_id})
    if not fsub:
        await fsubs_col.insert_one({
            "chat_id": chat_id,
            "invite_link": invite_link,
            "title": title
        })
        return True
    return False

async def del_fsub(chat_id):
    res = await fsubs_col.delete_one({"chat_id": chat_id})
    return res.deleted_count > 0
