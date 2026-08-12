import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON, LOGGER
from helper_func import encode


@Bot.on_message(
    filters.private
    & filters.user(ADMINS)
    & filters.incoming,
    group=1
)
async def channel_post(client: Client, message: Message):
    if message.text and message.text.startswith("/"):
        return
    if not message.media:
        return
    reply_text = await message.reply_text("<code>Tunggu Sebentar...</code>", quote=True)
    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except Exception as e:
        LOGGER(__name__).warning(e)
        await reply_text.edit_text("<b>Telah Terjadi Error...</b>")
        return
    base64_string = await encode([post_message.id])
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share Link", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )

    await reply_text.edit(
        f"<b>Link Sharing File Berhasil Di Buat :</b>\n\n{link}",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except Exception:
            pass


@Bot.on_message(
    filters.channel & filters.incoming & filters.chat(CHANNEL_ID) & ~filters.forwarded
)
async def new_post(client: Client, message: Message):

    if DISABLE_CHANNEL_BUTTON:
        return

    base64_string = await encode([message.id])
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share Link", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass
