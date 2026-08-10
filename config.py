import logging
import os


def strtobool(val):
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError(f"invalid truth value {val!r}")


from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv(".env")

# Bot token dari @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# API ID Anda dari my.telegram.org
APP_ID = int(os.environ.get("APP_ID") or 0)

# API Hash Anda dari my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# ID Channel Database
CHANNEL_ID = int(os.environ.get("CHANNEL_ID") or 0)

# NAMA OWNER
OWNER = os.environ.get("OWNER", "owner")

# Protect Content
PROTECT_CONTENT = strtobool(os.environ.get("PROTECT_CONTENT", "False"))

# Heroku Credentials for updater.
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)

# Custom Repo for updater.
UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "master")

import urllib.parse

def escape_db_uri(uri):
    if not uri:
        return uri

    prefix = ""
    if uri.startswith("mongodb://"):
        prefix = "mongodb://"
    elif uri.startswith("mongodb+srv://"):
        prefix = "mongodb+srv://"
    else:
        return uri

    rest = uri[len(prefix):]

    end_of_host = rest.find("/")
    if end_of_host == -1:
        end_of_host = rest.find("?")

    if end_of_host == -1:
        host_part = rest
    else:
        host_part = rest[:end_of_host]

    at_idx = host_part.rfind("@")
    if at_idx == -1:
        return uri

    credentials = host_part[:at_idx]

    colon_idx = credentials.find(":")
    if colon_idx == -1:
        user = urllib.parse.quote_plus(urllib.parse.unquote(credentials))
        escaped_credentials = user
    else:
        user = credentials[:colon_idx]
        password = credentials[colon_idx+1:]
        user = urllib.parse.quote_plus(urllib.parse.unquote(user))
        password = urllib.parse.quote_plus(urllib.parse.unquote(password))
        escaped_credentials = f"{user}:{password}"

    escaped_host_part = f"{escaped_credentials}@{host_part[at_idx+1:]}"

    if end_of_host == -1:
        return f"{prefix}{escaped_host_part}"
    else:
        return f"{prefix}{escaped_host_part}{rest[end_of_host:]}"

# Database
DB_URI = escape_db_uri(os.environ.get("DATABASE_URL", ""))

FORCE_SUB_1 = os.environ.get("FORCE_SUB_1", "0")
FORCE_SUB_2 = os.environ.get("FORCE_SUB_2", "0")

# ID dari Channel Atau Group Untuk Wajib Subscribenya
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL") or 0)
FORCE_SUB_GROUP = int(os.environ.get("FORCE_SUB_GROUP") or 0)

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS") or 4)

# Pesan Awalan /start
START_MSG = os.environ.get(
    "START_MESSAGE",
    "<b>Hello {first}</b>\n\n<b>Saya dapat menyimpan file pribadi di Channel Tertentu dan pengguna lain dapat mengaksesnya dari link khusus.</b>",
)
try:
    ADMINS = [int(x) for x in (os.environ.get("ADMINS", "").split())]
except ValueError:
    raise Exception("Daftar Admin Anda tidak berisi User ID Telegram yang valid.")

# Pesan Saat Memaksa Subscribe
FORCE_MSG = os.environ.get(
    "FORCE_SUB_MESSAGE",
    "<b>Hello {first}\n\nAnda harus bergabung di Channel/Grup saya Terlebih dahulu untuk Melihat File yang saya Bagikan\n\nSilakan Join Ke Channel & Group Terlebih Dahulu</b>",
)

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
