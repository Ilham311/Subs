import asyncio
import base64
import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from config import ADMINS, LOGGER
from config import FORCE_SUB_1, FORCE_SUB_2
from database.db import get_settings


async def check_fsub(client, user_id):
    if user_id in ADMINS:
        return True

    settings = await get_settings()
    db_fsubs = settings.get("force_sub_channels", [])

    fsubs = list(db_fsubs)
    if FORCE_SUB_1 and FORCE_SUB_1 != "0" and FORCE_SUB_1 not in fsubs:
        fsubs.append(FORCE_SUB_1)
    if FORCE_SUB_2 and FORCE_SUB_2 != "0" and FORCE_SUB_2 not in fsubs:
        fsubs.append(FORCE_SUB_2)

    if not fsubs:
        return True

    async def check_channel(fsub_id):
        try:
            member = await client.get_chat_member(chat_id=fsub_id, user_id=user_id)
            if member.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.RESTRICTED,
            ]:
                return False
            return True
        except UserNotParticipant:
            return False
        except Exception as e:
            LOGGER(__name__).warning(f"Error pada saat mengecek member di channel {fsub_id}: {e}")
            return True # If the bot fails to get member status (e.g., it is not an admin, or the channel is invalid), allow the user so they are not permanently blocked.

    results = await asyncio.gather(*(check_channel(fsub) for fsub in fsubs))
    return all(results)


async def is_subscribed(filter, client, update):
    user_id = update.from_user.id
    return await check_fsub(client, user_id)


subsall = filters.create(is_subscribed)


import secrets
from database.db import save_link, get_link

async def encode(message_ids):
    token = secrets.token_urlsafe(16)
    await save_link(token, message_ids)
    return token


async def decode(base64_string, db_channel_id=None):
    try:
        # Try fetching as a random token link first
        message_ids = await get_link(base64_string)
        if message_ids:
            return message_ids

        # If it is not a token, decode it as a legacy base64 string
        base64_string_padded = base64_string.strip("=")
        base64_bytes = (base64_string_padded + "=" * (-len(base64_string_padded) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        string = string_bytes.decode("ascii")

        # Process legacy numeric format: get-msg_id or get-start_id-end_id
        argument = string.split("-")
        if len(argument) == 3:
            start = int(argument[1])
            end = int(argument[2])
            if db_channel_id:
                start = start // abs(db_channel_id)
                end = end // abs(db_channel_id)
            if start <= end:
                return list(range(start, end + 1))
            else:
                return list(range(start, end - 1, -1))
        elif len(argument) == 2:
            msg_id = int(argument[1])
            if db_channel_id:
                msg_id = msg_id // abs(db_channel_id)
            return [msg_id]

        return []
    except Exception as e:
        LOGGER(__name__).warning(f"Error decoding link {base64_string}: {e}")
        return []


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
            msgs = []

        total_messages += len(temb_ids)
        if msgs:
            # Filter None to avoid adding invalid messages
            messages.extend([msg for msg in msgs if msg is not None])
    return messages


async def get_message_id(client, message):
    try:
        if (
            message.forward_from_chat
            and message.forward_from_chat.id == client.db_channel.id
        ):
            return message.forward_from_message_id
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
            return 0
    except Exception as e:
        LOGGER(__name__).warning(f"Error in get_message_id: {e}")
        return 0
