from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from database.db import update_settings, ban_user, unban_user, add_fsub, del_fsub

@Bot.on_message(filters.command("setstart") & filters.user(ADMINS))
async def set_start_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/setstart [pesan baru]`\nDukung HTML parsemode.")
    new_msg = message.text.split(None, 1)[1]
    await update_settings("start_msg", new_msg)
    await message.reply_text("Pesan Start berhasil diperbarui!")

@Bot.on_message(filters.command("setforce") & filters.user(ADMINS))
async def set_force_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/setforce [pesan baru]`\nDukung HTML parsemode.")
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

@Bot.on_message(filters.command("addfsub") & filters.user(ADMINS))
async def add_fsub_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/addfsub [chat_id]`\nPastikan bot sudah menjadi admin di chat tersebut.")
    try:
        chat_id = int(message.command[1])
        chat_info = await client.get_chat(chat_id)
        link = chat_info.invite_link
        if not link:
            link = await client.export_chat_invite_link(chat_id)

        added = await add_fsub(chat_id, link, chat_info.title)
        if added:
            await message.reply_text(f"Berhasil menambahkan {chat_info.title} ke daftar Force Sub!")
        else:
            await message.reply_text("Chat ini sudah ada di daftar Force Sub.")
    except Exception as e:
        await message.reply_text(f"Error: Gagal mendapatkan info chat. {e}")

@Bot.on_message(filters.command("delfsub") & filters.user(ADMINS))
async def del_fsub_cmd(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Penggunaan: `/delfsub [chat_id]`")
    try:
        chat_id = int(message.command[1])
        deleted = await del_fsub(chat_id)
        if deleted:
            await message.reply_text(f"Berhasil menghapus {chat_id} dari daftar Force Sub.")
        else:
            await message.reply_text("Chat tidak ditemukan di daftar Force Sub.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Bot.on_chat_join_request()
async def auto_approve(client: Bot, message):
    try:
        await client.approve_chat_join_request(message.chat.id, message.from_user.id)
    except Exception:
        pass
