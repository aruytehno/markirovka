# logger_config.py
import logging
from pathlib import Path
import sys
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Настройка логирования для всего проекта"""
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Основной логгер
    logger = logging.getLogger("markirovka")
    logger.setLevel(logging.DEBUG)

    # Форматтер с указанием файла и строки
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        log_dir / "markirovka.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Очищаем существующие обработчики
    logger.handlers.clear()

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Запрещаем передачу сообщений корневому логгеру
    logger.propagate = False

    return logger


# Инициализируем логгер
logger = setup_logging()
