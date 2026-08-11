from pyrogram.types import InlineKeyboardButton
from config import FORCE_SUB_1, FORCE_SUB_2
from database.db import get_settings


async def get_fsub_links(client):
    settings = await get_settings()
    db_fsubs = settings.get("force_sub_channels", [])

    fsubs = list(db_fsubs)
    if FORCE_SUB_1 and FORCE_SUB_1 != "0" and FORCE_SUB_1 not in fsubs:
        fsubs.append(FORCE_SUB_1)
    if FORCE_SUB_2 and FORCE_SUB_2 != "0" and FORCE_SUB_2 not in fsubs:
        fsubs.append(FORCE_SUB_2)

    links = []
    for i, fsub in enumerate(fsubs):
        try:
            fsub_id = fsub
            chat = await client.get_chat(fsub_id)
            link = chat.invite_link
            if not link:
                link = await client.export_chat_invite_link(fsub_id)
            title = chat.title
            links.append({"title": title, "invite_link": link, "index": i + 1})
        except Exception:
            # If bot can't get chat info, fallback to username if possible
            if isinstance(fsub_id, str) and not fsub_id.startswith("-100"):
                username = fsub_id.replace("@", "")
                links.append(
                    {
                        "title": f"Channel {i+1}",
                        "invite_link": f"https://t.me/{username}",
                        "index": i + 1,
                    }
                )
            else:
                links.append(
                    {"title": f"Channel {i+1}", "invite_link": "", "index": i + 1}
                )
    return links


async def start_button(client):
    fsubs = await get_fsub_links(client)
    buttons = []

    # Render all fsub buttons
    for fsub in fsubs:
        if fsub["invite_link"]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Join {fsub['title']}", url=fsub["invite_link"]
                    )
                ]
            )

    # Append default buttons
    buttons.append(
        [
            InlineKeyboardButton(text="Help & Command", callback_data="help"),
            InlineKeyboardButton(text="Close", callback_data="close"),
        ]
    )
    return buttons


async def fsub_button(client, message):
    fsubs = await get_fsub_links(client)
    buttons = []

    # Render all fsub buttons
    for fsub in fsubs:
        if fsub["invite_link"]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Join {fsub['title']}", url=fsub["invite_link"]
                    )
                ]
            )

    # Try again button
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Coba Lagi",
                    url=f"https://t.me/{client.username}?start={message.command[1]}",
                )
            ]
        )
    except IndexError:
        pass

    return buttons
