from pyrogram.types import InlineKeyboardButton
from database.db import get_fsubs

async def start_button(client):
    fsubs = await get_fsubs()
    buttons = []

    # Render all fsub buttons
    for fsub in fsubs:
        buttons.append([InlineKeyboardButton(text=f"Join {fsub.get('title', 'Channel')}", url=fsub['invite_link'])])

    # Append default buttons
    buttons.append([
        InlineKeyboardButton(text="Help & Command", callback_data="help"),
        InlineKeyboardButton(text="Close", callback_data="close"),
    ])
    return buttons


async def fsub_button(client, message):
    fsubs = await get_fsubs()
    buttons = []

    # Render all fsub buttons
    for fsub in fsubs:
        buttons.append([InlineKeyboardButton(text=f"Join {fsub.get('title', 'Channel')}", url=fsub['invite_link'])])

    # Try again button
    try:
        buttons.append([
            InlineKeyboardButton(
                text="Try again",
                url=f"https://t.me/{client.username}?start={message.command[1]}",
            )
        ])
    except IndexError:
        pass

    return buttons
