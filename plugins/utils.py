import os

from bot import Bot
from config import (
    LOGGER,
    ADMINS,
    CHANNEL_ID,
    FORCE_SUB_1,
    FORCE_SUB_2,
    OWNER,
    PROTECT_CONTENT,
    DISABLE_CHANNEL_BUTTON,
    UPSTREAM_BRANCH,
    TG_BOT_WORKERS,
    APP_ID,
    API_HASH,
    TG_BOT_TOKEN,
    DB_URI,
    HEROKU_API_KEY,
)
from database.db import get_settings
from pyrogram import filters
from pyrogram.types import Message


@Bot.on_message(filters.command("logs") & filters.user(ADMINS) & filters.private)
async def get_bot_logs(client: Bot, m: Message):
    bot_log_path = "logs.txt"
    if os.path.exists(bot_log_path):
        try:
            await m.reply_document(
                bot_log_path,
                quote=True,
                caption="<b>Ini Logs Bot ini</b>",
            )
        except Exception as e:
            # Do NOT remove the log file on send failure (J34)
            LOGGER(__name__).error(f"Gagal mengirim log file: {e}")
    else:
        await m.reply_text("❌ <b>Tidak ada log yang ditemukan!</b>")


@Bot.on_message(filters.command("vars") & filters.user(ADMINS) & filters.private)
async def varsFunc(client: Bot, message: Message):
    wait_msg = await message.reply_text("Tunggu Sebentar...")

    settings = await get_settings()
    fsubs = settings.get("force_sub_channels", [])
    auto_delete_time = settings.get("auto_delete_time", 0)

    def mask_secret(secret):
        if not secret:
            return "Not Set"
        s = str(secret)
        if len(s) <= 8:
            return "****"
        return f"{s[:4]}***{s[-4:]}"

    text = f"""<u><b>CONFIG VARS</b></u> @{client.username}
OWNER = <code>{OWNER}</code>
TG_BOT_WORKERS = <code>{TG_BOT_WORKERS}</code>
PROTECT_CONTENT = <code>{PROTECT_CONTENT}</code>
DISABLE_CHANNEL_BUTTON = <code>{DISABLE_CHANNEL_BUTTON}</code>
UPSTREAM_BRANCH = <code>{UPSTREAM_BRANCH}</code>
CHANNEL_ID = <code>{CHANNEL_ID}</code>
FORCE_SUB_1 = <code>{FORCE_SUB_1}</code>
FORCE_SUB_2 = <code>{FORCE_SUB_2}</code>

<u><b>DYNAMIC SETTINGS (DB)</b></u>
auto_delete_time = <code>{auto_delete_time}</code>
force_sub_channels count = <code>{len(fsubs)}</code>

<u><b>SECRETS (MASKED)</b></u>
TG_BOT_TOKEN = <code>{mask_secret(TG_BOT_TOKEN)}</code>
API_HASH = <code>{mask_secret(API_HASH)}</code>
APP_ID = <code>{mask_secret(APP_ID)}</code>
DATABASE_URL = <code>{mask_secret(DB_URI)}</code>
HEROKU_API_KEY = <code>{mask_secret(HEROKU_API_KEY)}</code>
    """
    await wait_msg.edit_text(text)
