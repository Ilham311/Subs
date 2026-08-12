import logging
import os


def strtobool(val):
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val!r}")


def get_int_env(key, default=None):
    val = os.environ.get(key)
    if not val:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{key}' tidak boleh kosong")
    try:
        return int(val)
    except ValueError:
        raise ValueError(
            f"Environment variable '{key}' harus berupa angka, tapi nilainya '{val}'"
        )


def normalize_chat_id(value):
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    if value.startswith("@"):
        return value
    if value.isalpha() or (
        any(c.isalpha() for c in value) and not value.startswith("-")
    ):
        return f"@{value}"

    # Handle numbers
    if value.startswith("-100"):
        return int(value)
    if value.startswith("-"):
        # Could be like -12345, check if we need to add 100
        if len(value) == 14 and value.startswith("-100"):
             return int(value)
        return int(f"-100{value[1:]}")
    if value.isdigit():
        if len(value) == 13 and value.startswith("100"):
            # Avoid double prefixing if it's already a 13-digit raw id starting with 100
            return int(f"-{value}")
        return int(f"-100{value}")

    return value


from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv(".env")

# Bot token dari @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# API ID Anda dari my.telegram.org
APP_ID = get_int_env("APP_ID")

# API Hash Anda dari my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# ID Channel Database
CHANNEL_ID = normalize_chat_id(os.environ.get("CHANNEL_ID"))

# NAMA OWNER (This is only a display username. Admin permissions come from ADMINS below)
OWNER = os.environ.get("OWNER", "owner")

# Protect Content
PROTECT_CONTENT = strtobool(os.environ.get("PROTECT_CONTENT", "False"))

# Heroku Credentials for updater.
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)

# Custom Repo for updater.
UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "master")

# Database
DB_URI = os.environ.get("DATABASE_URL", "")

FORCE_SUB_1 = normalize_chat_id(os.environ.get("FORCE_SUB_1", ""))
FORCE_SUB_2 = normalize_chat_id(os.environ.get("FORCE_SUB_2", ""))

TG_BOT_WORKERS = get_int_env("TG_BOT_WORKERS", default=4)

# Pesan Awalan /start
START_MSG = os.environ.get("START_MESSAGE")
if not START_MSG:
    START_MSG = "<b>Hello {first}</b>\n\n<b>Saya dapat menyimpan file pribadi di Channel Tertentu dan pengguna lain dapat mengaksesnya dari link khusus.</b>"

try:
    ADMINS = [int(x) for x in (os.environ.get("ADMINS", "").split())]
    if not ADMINS:
        logging.getLogger(__name__).warning("WARNING: ADMINS is empty. Bot will have no admins.")
except ValueError:
    raise Exception("Daftar Admin Anda tidak berisi User ID Telegram yang valid.")

# Pesan Saat Memaksa Subscribe
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE")
if not FORCE_MSG:
    FORCE_MSG = "<b>Hello {first}\n\nAnda harus bergabung di Channel/Grup saya Terlebih dahulu untuk Melihat File yang saya Bagikan\n\nSilakan Join Ke Channel & Group Terlebih Dahulu</b>"

# Atur Teks Kustom Anda di sini, Simpan (None) untuk Menonaktifkan Teks Kustom
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

# Setel True jika Anda ingin Menonaktifkan tombol Bagikan Kiriman Saluran Anda
DISABLE_CHANNEL_BUTTON = strtobool(os.environ.get("DISABLE_CHANNEL_BUTTON", "False"))

LOG_FILE_NAME = "logs.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
