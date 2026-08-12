# Force Subs Bot

Bot Telegram modern untuk menyimpan Posting atau File yang dapat Diakses melalui Link Khusus (File Sharing).

## 🚀 Fitur Utama
- **MongoDB Async Native:** Lebih cepat, database terpusat, & kuat untuk jutaan user.
- **Docker Ready:** Deploy mudah di server/VPS manapun tanpa error dependensi.
- **Multi-Force Sub Tanpa Batas:** Admin bisa setup channel wajib subscribe tak terbatas lewat command.
- **Auto-Approve Chat Join Request:** Terima request otomatis untuk channel/grup tertutup.
- **Pengaturan Dinamis (In-App):** Set pesan start, force sub, tanpa perlu merestart bot.

### Setup (Deploy via Docker)
1. Install Docker & Docker-Compose di VPS.
2. Edit file `.env` dan isikan konfigurasi bot (Token, API, MongoDB URL).
3. Jalankan perintah:
```bash
docker-compose up -d --build
```

### Variabel Lingkungan (`.env`)
- `API_HASH`: API HASH (my.telegram.org)
- `APP_ID`: APP ID (my.telegram.org)
- `TG_BOT_TOKEN`: Dari BotFather
- `OWNER`: Username Anda tanpa @
- `CHANNEL_ID`: ID Channel untuk menyimpan database
- `ADMINS`: Daftar ID (angka) Admin, pisahkan dengan spasi.
- `DATABASE_URL`: URI Koneksi MongoDB (Cluster / Local). **Catatan: Jika menggunakan docker-compose bawaan, url ini wajib diisi `mongodb://mongo:27017` bukan localhost.**
- `START_MESSAGE`: (Opsional)
- `FORCE_SUB_MESSAGE`: (Opsional)
- `PROTECT_CONTENT`: True / False (Cegah Forward)

### Perintah Pengguna
- `/start` : Memulai bot
- `/about` : Tentang bot
- `/help` : Bantuan perintah bot
- `/ping` : Cek ping bot
- `/uptime` : Cek uptime bot

### Perintah Admin
- `/broadcast` : Broadcast pesan ke semua pengguna (balas pesan).
- `/batch` : Membuat link sharing lebih dari satu file.
- `/genlink` : Membuat link sharing dari 1 file.
- `/users` : Melihat statistik pengguna bot.
- `/logs` : Melihat logs bot.
- `/vars` : Melihat variable bot.
- `/setstart [pesan]` : Mengubah pesan start secara langsung.
- `/setforce [pesan]` : Mengubah pesan Force Sub secara langsung.
- `/setdelete [detik]` : Mengatur waktu auto delete file (detik).
- `/ban [user_id]` : Banned pengguna bot.
- `/unban [user_id]` : Unban pengguna.
- `/addfsub [chat_id]` : Menambahkan channel ke daftar Wajib Subscribe.
- `/delfsub [chat_id]` : Menghapus channel dari daftar Wajib Subscribe.

### Changelog (Bug Fixes)
* R3: Fixed crashes in `/genlink` and `/batch` when forwarding from the DB channel due to Pyrogram missing `forward_from_message.id`.
* R4: Fixed silent crashes in `/start` caused by `None` or empty `start_msg` and `force_msg` settings.
* R5: Fixed cache corruption issue in `/addfsub` and `/delfsub` where mutating the in-memory array caused issues on DB write failures.
* R6: Ensured `/addfsub` correctly validates that the bot is an admin in the targeted channel before adding it to `force_sub_channels`.
* R7: Prevented plain text messages from admins from automatically generating share links in `channel_post`.
* R8: Fixed incorrect `broadcast` report totals by adding a skipped-admin counter.
