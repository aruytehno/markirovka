import os
import tempfile
from pathlib import Path
from typing import List, Tuple
import fitz
from logger_config import logger
from utils.pdf_utils import process_single_pdf


def get_pdf_with_codes(codes: List[str], pdf_folder: str) -> List[Tuple[int, str, bytes]]:
    """
    Возвращает список PDF с изображениями кодов, сгруппированных по товарам.

    Args:
        codes: Список кодов для поиска
        pdf_folder: Путь к папке с PDF файлами товаров

    Returns:
        List[Tuple[int, str, bytes]]: Список кортежей (количество кодов, название товара, PDF в байтах)
    """
    results = []

    # Получаем список папок товаров
    product_folders = [f for f in os.listdir(pdf_folder)
                       if os.path.isdir(os.path.join(pdf_folder, f))]

    for product_name in product_folders:
        product_path = os.path.join(pdf_folder, product_name)
        pdf_files = list(Path(product_path).rglob("*.pdf"))

        if not pdf_files:
            continue

        # Создаем временную папку для обработки
        with tempfile.TemporaryDirectory() as temp_dir:
            found_codes = []

            for pdf_path in pdf_files:
                try:
                    # Обрабатываем каждый PDF и собираем найденные коды
                    codes_found = process_single_pdf(
                        str(pdf_path), codes, temp_dir
                    )
                    found_codes.extend(codes_found)

                except Exception as e:
                    logger.error(f"Ошибка при обработке {pdf_path}: {e}")
                    continue

            if found_codes:
                # Объединяем все созданные PDF файлы в один
                output_doc = fitz.open()

                for pdf_file in Path(temp_dir).glob("*.pdf"):
                    if pdf_file.name.startswith("("):  # Пропускаем промежуточные файлы
                        doc = fitz.open(str(pdf_file))
                        output_doc.insert_pdf(doc)
                        doc.close()

                if len(output_doc) > 0:
                    # Сохраняем в байты
                    pdf_bytes = output_doc.tobytes()
                    results.append((len(found_codes), product_name, pdf_bytes))

                output_doc.close()

    return results