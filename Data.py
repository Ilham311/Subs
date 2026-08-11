from pyrogram.types import InlineKeyboardButton


class Data:
    HELP = """
<b> ❏ Perintah untuk Pengguna BOT
 ├ /start - Mulai Bot
 ├ /about - Tentang Bot ini
 ├ /help - Bantuan Perintah Bot ini
 ├ /ping - Cek ping bot
 └ /uptime - Cek uptime bot
 
 ❏ Perintah Untuk Admin BOT
 ├ /broadcast - Broadcast pesan ke semua pengguna (balas pesan)
 ├ /batch - Membuat link sharing lebih dari satu file
 ├ /genlink - Membuat link sharing dari 1 file
 ├ /users - Melihat statistik pengguna bot
 ├ /logs - Melihat logs bot
 ├ /vars - Melihat variable bot
 ├ /setstart - Mengubah pesan start secara langsung
 ├ /setforce - Mengubah pesan Force Sub secara langsung
 ├ /setdelete - Mengatur waktu auto delete file (detik)
 ├ /ban - Banned pengguna bot
 ├ /unban - Unban pengguna
 ├ /addfsub - Menambahkan channel ke daftar Wajib Subscribe
 └ /delfsub - Menghapus channel dari daftar Wajib Subscribe</b>
"""

    close = [[InlineKeyboardButton("close", callback_data="close")]]

    mbuttons = [
        [
            InlineKeyboardButton("help & command", callback_data="help"),
            InlineKeyboardButton("close", callback_data="close"),
        ],
    ]

    buttons = [
        [
            InlineKeyboardButton("about me", callback_data="about"),
            InlineKeyboardButton("close", callback_data="close"),
        ],
    ]

    ABOUT = """
<b>Tentang Bot ini:

@{} adalah Bot Telegram untuk menyimpan Postingan atau File yang dapat Diakses melalui Link Khusus.

 • Owner: @{}</b>
"""
