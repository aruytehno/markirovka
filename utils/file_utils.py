import shutil
from datetime import datetime
from typing import List

from config import RESULTS_FOLDER
from logger_config import logger


import os

def get_available_products(pdf_folder: str) -> list[str]:
    """Возвращает список подпапок в указанной директории"""
    if not os.path.exists(pdf_folder):
        return []
    return [f for f in os.listdir(pdf_folder)
            if os.path.isdir(os.path.join(pdf_folder, f))]


def clear_directory(directory: str) -> None:
    """
    Полностью очищает указанную директорию (удаляет и заново создает).

    Args:
        directory: Путь к директории для очистки
    """
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logger.debug(f"Очищена директория: {directory}")

        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Создана директория: {directory}")
    except Exception as e:
        logger.error(f"Ошибка при очистке директории {directory}: {e}", exc_info=True)


def read_codes_from_folder(folder_path: str) -> List[str]:
    """
    Чтение всех кодов из txt файлов в указанной папке.

    Args:
        folder_path: Путь к папке с txt файлами кодов

    Returns:
        List[str]: Список уникальных кодов из всех файлов
    """
    codes = set()
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        code = line.strip()
                        if code:
                            codes.add(code)
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    return list(codes)




def format_validation_results(results):
    """Форматирование результатов проверки"""
    lines = []
    lines.append("Результаты проверки кодов:")
    lines.append("=" * 60)

    for i, result in enumerate(results, 1):
        status = result.get('status_text', 'Неизвестный статус')
        product = result.get('product_name', 'Неизвестный продукт')
        lines.append(f"{i}. {result['code']}: {status} [{product}]")

    # Добавляем статистику
    valid_count = sum(1 for r in results if r.get('found') and r.get('status') == 'INTRODUCED')
    invalid_count = len(results) - valid_count

    lines.append("=" * 60)
    lines.append(f"Итоги: ✅ {valid_count} валидных, ❌ {invalid_count} невалидных")

    return "\n".join(lines)


def save_validation_report(results):
    """Сохранение отчета в файл"""
    # Создаем папку results если не существует
    RESULTS_FOLDER.mkdir(exist_ok=True)

    # Генерируем имя файла с timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"validation_results_{timestamp}.txt"
    filepath = RESULTS_FOLDER / filename

    # Форматируем и сохраняем результаты
    report_text = format_validation_results(results)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_text)

    logger.info(f"Отчет сохранен в файл: {filepath}")
