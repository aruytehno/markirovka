import os
from typing import List
from infrastructure.database import MarkingCodeDB
from infrastructure.api_crpt import check_code
from utils.file_utils import read_codes_from_folder
from logger_config import logger


def get_free_codes(product_name: str, quantity: int, pdf_folder: str) -> List[str]:
    """
    Возвращает N свободных кодов для указанного товара.

    Args:
        product_name: Название папки-товара
        quantity: Требуемое количество кодов
        pdf_folder: Путь к папке с PDF файлами товаров

    Returns:
        List[str]: Список свободных кодов для обработки
    """
    # Инициализация БД
    db = MarkingCodeDB()

    # 1. Проверяем старые коды в обработке (>7 дней)
    logger.info(f"Проверка старых кодов в обработке для товара: {product_name}")
    db.check_old_processed_codes()

    # 2. Получаем доступные коды из БД
    available_codes = db.get_available_codes(product_name, quantity)
    logger.info(f"Найдено {len(available_codes)} доступных кодов в БД")

    # 3. Если недостаточно кодов, ищем дополнительные
    if len(available_codes) < quantity:
        needed = quantity - len(available_codes)
        logger.info(f"Требуется дополнительно {needed} кодов")

        # Получаем путь к папке товара
        product_path = os.path.join(pdf_folder, product_name)
        if not os.path.exists(product_path):
            logger.error(f"Папка товара не найдена: {product_path}")
            return available_codes[:quantity]

        # Читаем все коды из файлов товара
        all_codes = read_codes_from_folder(product_path)
        logger.info(f"Прочитано {len(all_codes)} кодов из файлов товара")

        # Ищем новые коды
        new_codes = []
        for code in all_codes:
            if len(new_codes) >= needed:
                break

            # Пропускаем коды, которые уже в available_codes
            if code in available_codes:
                continue

            # Проверяем статус кода
            code_info = db.get_code_info(code)
            if code_info:
                # Пропускаем коды с неудачными статусами
                if code_info.get('status') not in [None, 'INTRODUCED']:
                    continue
                # Пропускаем коды в обработке
                if code_info.get('in_process'):
                    continue

            # Проверяем код через API
            logger.info(f"Проверка кода через API: {code}")
            result = check_code(code, db)

            # Если код в обороте, добавляем его
            if result.get('status') == 'INTRODUCED':
                new_codes.append(code)
                logger.info(f"Добавлен новый код: {code}")

        # Добавляем новые коды к доступным
        available_codes.extend(new_codes)

    # 4. Помечаем коды как переданные в обработку
    if available_codes:
        selected_codes = available_codes[:quantity]
        if db.mark_codes_as_processing(selected_codes):
            logger.info(f"Помечено {len(selected_codes)} кодов как переданные в обработку")
            return selected_codes
        else:
            logger.error("Ошибка при отметке кодов как в обработке")
            return []

    logger.warning("Не найдено доступных кодов для обработки")
    return []