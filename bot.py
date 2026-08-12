import sys

import pyromod.listen
from pyrogram import Client, enums

from config import (
    API_HASH,
    APP_ID,
    CHANNEL_ID,
    FORCE_SUB_1,
    FORCE_SUB_2,
    LOGGER,
    OWNER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
)


class Bot(Client):
    def __init__(self):
        super().__init__(
            "Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        from database.db import ensure_connection
        try:
            await ensure_connection()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Gagal terhubung ke MongoDB. Bot berhenti. Error: {e}")
            sys.exit(1)

        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.username = usr_bot_me.username
            self.namebot = usr_bot_me.first_name
            self.LOGGER(__name__).info(
                f"TG_BOT_TOKEN detected!\n┌ First Name: {self.namebot}\n└ Username: @{self.username}\n——"
            )
        except Exception as a:
            self.LOGGER(__name__).warning(f"Error pada saat start: {a}")
            self.LOGGER(__name__).info("Bot Berhenti. Cek konfigurasi Anda.")
            sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(
                chat_id=db_channel.id, text="Test Message", disable_notification=True
            )
            await test.delete()
            self.LOGGER(__name__).info(
                f"CHANNEL_ID Database detected!\n┌ Title: {db_channel.title}\n└ Chat ID: {db_channel.id}\n——"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error channel database: {e}")
            self.LOGGER(__name__).warning(
                f"Pastikan @{self.username} adalah admin di Channel DataBase anda, CHANNEL_ID Saat Ini: {CHANNEL_ID}"
            )
            self.LOGGER(__name__).info("Bot Berhenti. Cek konfigurasi Anda.")
            sys.exit()

        self.set_parse_mode(enums.ParseMode.HTML)

        from database.db import get_settings
        settings = await get_settings()
        fsubs = settings.get("force_sub_channels", [])

        active_fsubs = list(fsubs)
        if FORCE_SUB_1 and FORCE_SUB_1 != "0" and FORCE_SUB_1 not in active_fsubs:
            active_fsubs.append(FORCE_SUB_1)
        if FORCE_SUB_2 and FORCE_SUB_2 != "0" and FORCE_SUB_2 not in active_fsubs:
            active_fsubs.append(FORCE_SUB_2)

        self.LOGGER(__name__).info(
            f"[🔥 BERHASIL DIAKTIFKAN! 🔥]\n\nBot: {self.namebot} (@{self.username})\nJumlah Force-Sub Aktif: {len(active_fsubs)}\nBot dijalankan oleh @{OWNER}"
        )

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
