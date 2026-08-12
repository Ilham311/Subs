from pyrogram.types import InlineKeyboardButton
from config import FORCE_SUB_1, FORCE_SUB_2
from database.db import get_settings, update_settings

_cached_invite_links = {}

async def get_fsub_links(client):
    settings = await get_settings()
    db_fsubs = settings.get("force_sub_channels", [])

    fsubs = list(db_fsubs)
    if FORCE_SUB_1 and FORCE_SUB_1 != "0" and FORCE_SUB_1 not in fsubs:
        fsubs.append(FORCE_SUB_1)
    if FORCE_SUB_2 and FORCE_SUB_2 != "0" and FORCE_SUB_2 not in fsubs:
        fsubs.append(FORCE_SUB_2)

    links = []
    cached_db_links = settings.get("invite_links_cache", {})

    # Merge DB cache with in-memory cache
    global _cached_invite_links
    for k, v in cached_db_links.items():
        if k not in _cached_invite_links:
            _cached_invite_links[k] = v

    for i, fsub in enumerate(fsubs):
        try:
            fsub_id = fsub
            fsub_key = str(fsub_id)
            title = f"Channel {i+1}"

            # Use cache if available
            if fsub_key in _cached_invite_links:
                cached_data = _cached_invite_links[fsub_key]
                links.append({"title": cached_data.get("title", title), "invite_link": cached_data.get("link"), "index": i + 1})
                continue

            chat = await client.get_chat(fsub_id)
            title = chat.title
            link = chat.invite_link

            if not link:
                # Use create_chat_invite_link instead of export to avoid revoking
                try:
                    invite = await client.create_chat_invite_link(chat_id=fsub_id)
                    link = invite.invite_link
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Gagal membuat invite link untuk channel {fsub_id}: {e}")
                    link = "" # Cannot generate link

            if link:
                _cached_invite_links[fsub_key] = {"title": title, "link": link}
                # We update the DB cache. We fetch current settings again to avoid overwriting other changes
                current_settings = await get_settings()
                db_cache = dict(current_settings.get("invite_links_cache", {}))
                db_cache[fsub_key] = {"title": title, "link": link}
                await update_settings("invite_links_cache", db_cache)
                links.append({"title": title, "invite_link": link, "index": i + 1})
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error mengambil chat {fsub_id}: {e}")
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
