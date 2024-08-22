import os
import glob
from PyPDF2 import PdfReader, PdfWriter


def add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_pdf_path):
    # Создаем объект PdfReader для водяного знака и первой страницы водяного знака
    watermark_reader = PdfReader(watermark_pdf_path)
    watermark_page = watermark_reader.pages[0]
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    i = 0
    total_pages = len(pdf_reader.pages)

    # Проходим по каждой странице входного PDF и добавляем водяной знак
    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)
        i = i + 1

    with open(output_pdf_path, 'wb') as out_file:
        pdf_writer.write(out_file)
    return i, total_pages


def fix_lines():
    # Получаем список всех PDF-файлов в папке input
    pdf_files = [f for f in glob.glob(os.path.join('input', "*.pdf"))]

    # Проверяем, есть ли файлы в папке input
    if not pdf_files:
        print('Папка "input" пуста. Нет файлов для обработки.')
    else:
        # Обрабатываем каждый файл
        for pdf_file in pdf_files:
            print(f'\nОбрабатывается: {pdf_file}')
            total_pages, processed_pages = add_watermark_to_pdf(
                pdf_file,
                os.path.join('out', os.path.basename(pdf_file)),
                'watermark.pdf'
            )
            print(f'Обработано: {processed_pages} из {total_pages} страниц.\n')