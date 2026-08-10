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
2. Edit file `config.env` dan isikan konfigurasi bot (Token, API, MongoDB URL).
3. Jalankan perintah:
```bash
docker-compose up -d --build
```

### Variabel Lingkungan (`config.env`)
- `API_HASH`: API HASH (my.telegram.org)
- `APP_ID`: APP ID (my.telegram.org)
- `TG_BOT_TOKEN`: Dari BotFather
- `OWNER`: Username Anda tanpa @
- `CHANNEL_ID`: ID Channel untuk menyimpan database
- `ADMINS`: Daftar ID (angka) Admin, pisahkan dengan spasi.
- `DATABASE_URL`: URI Koneksi MongoDB (Cluster / Local)
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
- `/addfsub [chat_id]` : Menambahkan channel ke daftar Wajib Subscribe.
- `/delfsub [chat_id]` : Menghapus channel dari daftar Wajib Subscribe.
- `/setstart [pesan]` : Mengubah pesan start secara langsung.
- `/setforce [pesan]` : Mengubah pesan Force Sub secara langsung.
- `/ban [user_id]` : Banned pengguna bot.
- `/unban [user_id]` : Unban pengguna.
- `/batch` : Membuat link sharing lebih dari satu file.
- `/genlink` : Membuat link sharing dari 1 file.

## 👨🏻‍💻 Credits
- Dan for Pyrogram
- Risman for File-Sharing-Man
- CodeXBotz for File-Sharing-Bot
- Poocong for ForceSubs

**Berikan Bintang Repo ini jika Anda menyukainya ⭐⭐⭐⭐⭐**
