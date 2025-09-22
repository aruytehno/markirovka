from pathlib import Path
import os
import fitz
from logger_config import logger

def process_single_pdf(pdf_path: str, codes_list: list, out_folder: str,
                       fixed_width=75, expand_y_top=85, expand_y_bottom=10):
    """
    Обрабатывает один PDF-файл
    """
    logger.debug(f"Начало обработки PDF: {pdf_path}")

    doc = fitz.open(pdf_path)
    out_doc = fitz.open()
    found_codes = []  # Список найденных кодов в этом PDF

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))

        page_codes = []

        for upper_rect, lower_rect, code_text in find_code_rects(blocks, codes_list):
            # Центрируем по горизонтали и задаем фиксированную ширину
            center_x = (min(upper_rect.x0, lower_rect.x0) + max(upper_rect.x1, lower_rect.x1)) / 2
            new_rect = fitz.Rect(
                center_x - fixed_width / 2,
                upper_rect.y0 - expand_y_top,
                center_x + fixed_width / 2,
                lower_rect.y1 + expand_y_bottom
            )

            # Логирование размера
            logger.debug(f"Код: {code_text}")
            logger.debug(
                f"new_rect (точки): x0={new_rect.x0:.2f}, y0={new_rect.y0:.2f}, x1={new_rect.x1:.2f}, y1={new_rect.y1:.2f}")
            logger.debug(
                f"new_rect (мм): x0={new_rect.x0 / 2.835:.2f}, y0={new_rect.y0 / 2.835:.2f}, x1={new_rect.x1 / 2.835:.2f}, y1={new_rect.y1 / 2.835:.2f}")
            logger.debug(
                f"ширина={new_rect.width:.2f}pt ({new_rect.width / 2.835:.2f}мм), высота={new_rect.height:.2f}pt ({new_rect.height / 2.835:.2f}мм)")

            # Создаем новую страницу
            new_page = out_doc.new_page(width=new_rect.width, height=new_rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page_num - 1, clip=new_rect)
            page_codes.append(code_text)
            found_codes.append(code_text)

        if page_codes:
            logger.info(f"Страница {page_num}: найдено {len(page_codes)} кодов: {page_codes}")

    # Сохраняем результат, если найдены коды
    if len(out_doc) > 0:
        output_filename = f"({len(out_doc)})_{Path(pdf_path).stem}.pdf"
        output_path = os.path.join(out_folder, output_filename)
        out_doc.save(output_path)
        logger.info(f"Сохранено {len(out_doc)} страниц в {output_path}")

    doc.close()
    out_doc.close()

    logger.debug(f"Завершение обработки PDF: {pdf_path}, найдено кодов: {len(found_codes)}")
    return found_codes


def find_code_rects(blocks, codes_list):
    """
    Находит прямоугольники, содержащие коды
    """
    # Используем set для более быстрого поиска
    codes_set = set(codes_list)
    results = []

    for i, upper_block in enumerate(blocks):
        upper_text = upper_block[4].strip()
        for lower_block in blocks[i + 1:]:
            lower_text = lower_block[4].strip()
            full_code = upper_text + lower_text
            if full_code in codes_set:
                results.append((fitz.Rect(upper_block[:4]), fitz.Rect(lower_block[:4]), full_code))
                break
    return results