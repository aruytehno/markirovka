import os
import glob
from PyPDF2 import PdfReader, PdfWriter


def fix_lines(input_folder, out_folder, watermark_pdf_path, file_type):
    # Получаем список всех PDF-файлов
    pdf_files = [f for f in glob.glob(os.path.join(input_folder, file_type))]

    # Проверяем, есть ли файлы в папке input
    if not pdf_files:
        print('Папка "input" пуста. Нет файлов для обработки.')
    else:
        # Обрабатываем каждый файл
        for pdf_file in pdf_files:
            print(f'\nОбрабатывается: {pdf_file}')

            # Создаем объект PdfReader для водяного знака и первой страницы водяного знака
            watermark_reader = PdfReader(watermark_pdf_path)
            watermark_page = watermark_reader.pages[0]
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            i = 0
            total_pages = len(pdf_reader.pages)

            # Проходим по каждой странице входного PDF и добавляем водяной знак
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)
                i = i + 1

            with open(os.path.join(out_folder, os.path.basename(pdf_file)), 'wb') as out_file:
                pdf_writer.write(out_file)
            print(f'Обработано: {i} из {total_pages} страниц.\n')