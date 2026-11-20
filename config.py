"""
Настройки проекта.

Секреты (токен бота) храним не в коде, а в файле .env.
Для работы скопируйте .env.example в .env и укажите свой токен.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Папка, в которой лежит этот файл (корень проекта).
BASE_DIR = Path(__file__).resolve().parent

# Загружаем переменные из файла .env (если он существует).
load_dotenv(BASE_DIR / ".env")

# Токен Telegram-бота, который выдаёт @BotFather.
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден BOT_TOKEN.\n"
        "Создайте файл .env в папке проекта и добавьте строку:\n"
        "BOT_TOKEN=ваш_токен_от_BotFather"
    )

# Необязательный прокси для доступа к api.telegram.org.
# Примеры: socks5://127.0.0.1:1080 или http://user:pass@host:port
PROXY_URL = os.getenv("PROXY_URL", "").strip() or None

# Папка для файла базы данных.
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Путь к базе SQLite. Можно переопределить в .env через DB_PATH.
_db_path_value = os.getenv("DB_PATH", "").strip()
DB_PATH = Path(_db_path_value) if _db_path_value else DATA_DIR / "tasks.db"

# Если указан относительный путь (например, data/tasks.db),
# считаем его относительно папки проекта, а не текущей папки запуска.
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH
