import os
from pathlib import Path
from dotenv import load_dotenv  # Добавьте эту строку

# Загружаем переменные окружения из .env файла
load_dotenv()  # Добавьте эту строку

# ==================== ПУТИ К ФАЙЛАМ И ПАПКАМ ====================
BASE_DIR = Path(__file__).parent

# База данных
DB_PATH = BASE_DIR / "data" / "marking_codes.db"

# Папки с файлами
PDF_FOLDER = BASE_DIR / "data" / "pdf_files"
RESULTS_FOLDER = BASE_DIR / "data" / "results"

# Файлы
DATAMATRIX_FILE = BASE_DIR / "data" / "datamatrix.txt"

# ==================== НАСТРОЙКИ БОТА ====================
# Токен бота (загружается из .env)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")