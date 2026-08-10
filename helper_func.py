import asyncio
import base64
import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from config import ADMINS, LOGGER
from config import FORCE_SUB_1, FORCE_SUB_2


async def check_fsub(client, user_id):
    if user_id in ADMINS:
        return True

    fsubs = []
    if FORCE_SUB_1 and FORCE_SUB_1 != "0":
        fsubs.append(FORCE_SUB_1)
    if FORCE_SUB_2 and FORCE_SUB_2 != "0":
        fsubs.append(FORCE_SUB_2)

    if not fsubs:
        return True

    for fsub in fsubs:
        try:
            # Cast to int if it's a numeric chat ID string
            try:
                fsub_id = int(fsub)
            except ValueError:
                fsub_id = fsub

            member = await client.get_chat_member(chat_id=fsub_id, user_id=user_id)
            if member.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
            ]:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            # Jika error lain (bot dikeluarkan dari channel, dll), anggap saja channel itu invalid, lanjut
            continue

    return True


async def is_subscribed(filter, client, update):
    user_id = update.from_user.id
    return await check_fsub(client, user_id)


subsall = filters.create(is_subscribed)


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


async def decode(base64_string):
    base64_string = base64_string.strip(
        "="
    )  # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string


async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages : total_messages + 200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except Exception as e:
            LOGGER(__name__).error(f"Error: {e}")
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    if (
        message.forward_from_chat
        and message.forward_from_chat.id == client.db_channel.id
    ):
        return message.forward_from_message.id
    elif message.forward_from_chat or message.forward_sender_name or not message.text:
        return 0
    else:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        elif channel_id == client.db_channel.username:
            return msg_id
