from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS, normalize_chat_id
from database.db import update_settings, get_settings, ban_user, unban_user


@Bot.on_message(filters.command("setstart") & filters.user(ADMINS))
async def set_start_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Penggunaan: `/setstart [pesan baru]`\nDukung HTML parsemode."
        )
    new_msg = message.text.split(None, 1)[1]
    await update_settings("start_msg", new_msg)
    await message.reply_text("Pesan Start berhasil diperbarui!")


@Bot.on_message(filters.command("setforce") & filters.user(ADMINS))
async def set_force_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Penggunaan: `/setforce [pesan baru]`\nDukung HTML parsemode."
        )
    new_msg = message.text.split(None, 1)[1]
    await update_settings("force_msg", new_msg)
    await message.reply_text("Pesan Force Sub berhasil diperbarui!")


@Bot.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/ban [user_id]`")
    try:
        user_id = int(message.command[1])
        await ban_user(user_id)
        await message.reply_text(f"User {user_id} berhasil dibanned.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Bot.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/unban [user_id]`")
    try:
        user_id = int(message.command[1])
        await unban_user(user_id)
        await message.reply_text(f"User {user_id} berhasil di-unban.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Bot.on_chat_join_request()
async def auto_approve(client: Bot, message):
    try:
        await client.approve_chat_join_request(message.chat.id, message.from_user.id)
    except Exception:
        pass


@Bot.on_message(filters.command("setdelete") & filters.user(ADMINS))
async def set_delete_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Penggunaan: `/setdelete [detik]`\nKetik `/setdelete 0` untuk menonaktifkan."
        )
    try:
        detik = int(message.command[1])
        await update_settings("auto_delete_time", detik)
        if detik > 0:
            await message.reply_text(f"Auto-delete berhasil diatur ke {detik} detik.")
        else:
            await message.reply_text("Auto-delete berhasil dinonaktifkan.")
    except ValueError:
        await message.reply_text("Harap masukkan angka yang valid.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Bot.on_message(filters.command("addfsub") & filters.user(ADMINS))
async def add_fsub_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Penggunaan: `/addfsub [chat_id/username]`"
        )
    chat_id = normalize_chat_id(message.command[1])

    settings = await get_settings()
    fsubs = settings.get("force_sub_channels", [])
    if chat_id in fsubs:
        return await message.reply_text("Channel tersebut sudah ada di daftar Wajib Subscribe.")

    fsubs.append(chat_id)
    await update_settings("force_sub_channels", fsubs)
    await message.reply_text(f"Berhasil menambahkan {chat_id} ke daftar Wajib Subscribe.")


@Bot.on_message(filters.command("delfsub") & filters.user(ADMINS))
async def del_fsub_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Penggunaan: `/delfsub [chat_id/username]`"
        )
    chat_id = normalize_chat_id(message.command[1])

    settings = await get_settings()
    fsubs = settings.get("force_sub_channels", [])
    if chat_id not in fsubs:
        return await message.reply_text("Channel tersebut tidak ada di daftar Wajib Subscribe.")

    fsubs.remove(chat_id)
    await update_settings("force_sub_channels", fsubs)
    await message.reply_text(f"Berhasil menghapus {chat_id} dari daftar Wajib Subscribe.")
