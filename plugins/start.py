import asyncio
from datetime import datetime, timezone
from time import time

from bot import Bot
from config import (
    LOGGER,
    ADMINS,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    FORCE_MSG,
    PROTECT_CONTENT,
    START_MSG,
)
from database.db import add_user, get_all_users, get_all_users_count, get_settings, is_banned, delete_user
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton

from helper_func import decode, get_messages, subsall

from .button import fsub_button, start_button

START_TIME = datetime.now(timezone.utc)
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)


@Bot.on_message(filters.command("start") & filters.private & subsall)
async def start_command(client: Bot, message: Message):
    id = message.from_user.id
    if await is_banned(id):
        return await message.reply("Anda telah dibanned dari menggunakan bot ini.")
    user_name = f"@{message.from_user.username}" if message.from_user.username else None

    try:
        await add_user(id, user_name)
    except:
        pass
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except Exception as e:
            LOGGER(__name__).error(f"Error: {e}")
            return

        # `decode` now returns a list of message_ids directly (or an empty list if invalid)
        ids = await decode(base64_string, client.db_channel.id)

        if not ids:
            return await message.reply("Link tidak valid.")

        temp_msg = await message.reply("<code>Tunggu Sebentar...</code>")
        try:
            messages = list(await get_messages(client, ids))
        except Exception as e:
            LOGGER(__name__).error(f"Error: {e}")
            await message.reply_text("<b>Telah Terjadi Error </b>🥺")
            return
        await temp_msg.delete()

        if not messages:
            return await message.reply("File tidak ditemukan atau sudah dihapus.")

        settings = await get_settings()
        auto_delete_time = settings.get("auto_delete_time", 0)
        sent_messages = []

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name,
                )

            else:
                caption = msg.caption.html if msg.caption else ""

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
            try:
                s_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )
                sent_messages.append(s_msg)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                s_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )
                sent_messages.append(s_msg)
            except Exception as e:
                LOGGER(__name__).error(f"Error: {e}")
                pass

        if auto_delete_time > 0 and sent_messages:

            async def delete_msgs(msgs, delay_time):
                await asyncio.sleep(delay_time)
                for m in msgs:
                    try:
                        await m.delete()
                    except Exception:
                        pass

            task = asyncio.create_task(delete_msgs(sent_messages, auto_delete_time))
            if not hasattr(client, "_delete_tasks"):
                client._delete_tasks = set()
            client._delete_tasks.add(task)
            task.add_done_callback(client._delete_tasks.discard)

            try:
                bot_username = client.username
                await message.reply_text(
                    f"⚠️ <b>Peringatan:</b> Pesan di atas akan dihapus otomatis dalam waktu {auto_delete_time} detik.\n\nSilahkan forward atau simpan file jika diperlukan.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Dapatkan Ulang File",
                                    url=f"https://t.me/{bot_username}?start={base64_string}",
                                )
                            ]
                        ]
                    ),
                    quote=True,
                )
            except Exception as e:
                LOGGER(__name__).error(f"Error sending auto-delete warning: {e}")
                pass

    else:
        out = await start_button(client)
        settings = await get_settings()
        start_msg = settings.get("start_msg", START_MSG)
        try:
            formatted_text = start_msg.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=(
                    f"@{message.from_user.username}"
                    if message.from_user.username
                    else None
                ),
                mention=message.from_user.mention,
                id=message.from_user.id,
            )
        except (KeyError, IndexError, ValueError):
            formatted_text = start_msg

        await message.reply_text(
            text=formatted_text,
            reply_markup=InlineKeyboardMarkup(out),
            disable_web_page_preview=True,
            quote=True,
        )

    return


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Bot, message: Message):
    if await is_banned(message.from_user.id):
        return await message.reply("Anda telah dibanned dari menggunakan bot ini.")

    buttons = await fsub_button(client, message)
    settings = await get_settings()
    force_msg = settings.get("force_msg", FORCE_MSG)
    try:
        formatted_text = force_msg.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=(
                f"@{message.from_user.username}" if message.from_user.username else None
            ),
            mention=message.from_user.mention,
            id=message.from_user.id,
        )
    except (KeyError, IndexError, ValueError):
        formatted_text = force_msg

    await message.reply(
        text=formatted_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
    )


@Bot.on_message(filters.command(["users", "stats"]) & filters.user(ADMINS))
async def get_users_stats(client: Bot, message: Message):
    msg = await client.send_message(
        chat_id=message.chat.id, text="<code>Processing ...</code>"
    )
    total_users = await get_all_users_count()
    await msg.edit(f"{total_users} <b>Pengguna menggunakan bot ini</b>")


@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        total = await get_all_users_count()
        broadcast_msg = message.reply_to_message
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        current = 0

        pls_wait = await message.reply(
            "<code>[~] Broadcasting Message Tunggu Sebentar...</code>"
        )

        sem = asyncio.Semaphore(50)  # Limit concurrent broadcasts

        async def send_msg(user_id):
            nonlocal successful, blocked, deleted, unsuccessful
            if user_id in ADMINS:
                return
            async with sem:
                for retry in range(3):
                    try:
                        await broadcast_msg.copy(user_id, protect_content=PROTECT_CONTENT)
                        successful += 1
                        return
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        continue
                    except UserIsBlocked:
                        blocked += 1
                        try:
                            await delete_user(user_id)
                        except Exception:
                            pass
                        return
                    except InputUserDeactivated:
                        deleted += 1
                        try:
                            await delete_user(user_id)
                        except Exception:
                            pass
                        return
                    except Exception as e:
                        LOGGER(__name__).error(f"Error: {e}")
                        unsuccessful += 1
                        return

                # If we exhausted 3 retries for FloodWait
                unsuccessful += 1

        # Pre-fetch all user IDs to avoid Mongo cursor timeout on large broadcasts
        user_ids = []
        async for row in get_all_users():
            user_ids.append(int(row["id"]))

        tasks = []
        for chat_id in user_ids:
            current += 1
            tasks.append(asyncio.create_task(send_msg(chat_id)))

            if current % 100 == 0:
                await asyncio.gather(*tasks)
                tasks = []
                try:
                    await pls_wait.edit(
                        f"<code>[~] Broadcasting... {current}/{total} users processed.</code>"
                    )
                except Exception:
                    pass

        if tasks:
            await asyncio.gather(*tasks)

        status = f"""<b><u>Laporan Broadcast Selesai</u>
Total Pengguna: <code>{total}</code>
Berhasil Terkirim: <code>{successful}</code>
Gagal Terkirim: <code>{unsuccessful}</code>
User Memblokir Bot (Dihapus dari DB): <code>{blocked}</code>
Akun Terhapus (Dihapus dari DB): <code>{deleted}</code></b>"""
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(
            "<code>Harap reply ke pesan yang ingin di broadcast!</code>"
        )
        await asyncio.sleep(5)
        await msg.delete()


@Bot.on_message(filters.command("ping") & filters.private)
async def ping_pong(client, m: Message):
    start = time()
    current_time = datetime.now(timezone.utc)
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await m.reply_text("Pinging...")
    delta_ping = time() - start
    await m_reply.edit_text(
        "<b>PONG!!</b>🏓 \n"
        f"<b>• Pinger -</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"<b>• Uptime -</b> <code>{uptime}</code>\n"
    )


@Bot.on_message(filters.command("uptime") & filters.private)
async def get_uptime(client, m: Message):
    current_time = datetime.now(timezone.utc)
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        "🤖 <b>Bot Status:</b>\n"
        f"• <b>Uptime:</b> <code>{uptime}</code>\n"
        f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )
