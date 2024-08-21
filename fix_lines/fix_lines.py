import os
import glob
from PyPDF2 import PdfReader, PdfWriter


def add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_pdf_path):
    """
    Добавляет водяной знак ко всем страницам PDF-файла.

    :param input_pdf_path: Путь к исходному PDF-файлу, который нужно обработать.
    :param output_pdf_path: Путь к выходному PDF-файлу с добавленным водяным знаком.
    :param watermark_pdf_path: Путь к PDF-файлу с водяным знаком.
    :return: Кортеж с количеством обработанных страниц и общим числом страниц.
    """
    # Создаем объект PdfReader для водяного знака и первой страницы водяного знака
    watermark_reader = PdfReader(watermark_pdf_path)
    watermark_page = watermark_reader.pages[0]

    # Создаем объект PdfReader для входного PDF и PdfWriter для записи выходного PDF
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    total_pages = len(pdf_reader.pages)

    # Проходим по каждой странице входного PDF и добавляем водяной знак
    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)

    # Записываем результат в выходной файл
    with open(output_pdf_path, 'wb') as out_file:
        pdf_writer.write(out_file)

    return total_pages, total_pages


if __name__ == "__main__":
    list_folders = ['input', 'out']
    for folder in list_folders:
        if not os.path.exists(folder):
            print('Создана папка', folder)
            os.makedirs(folder)

    # Получаем список всех PDF-файлов в папке input
    pdf_files = [f for f in glob.glob(os.path.join('input', "*.pdf"))]

    # Обрабатываем каждый файл
    for pdf_file in pdf_files:
        print(f'\nОбрабатывается: {pdf_file}')
        total_pages, processed_pages = add_watermark_to_pdf(
            pdf_file,
            os.path.join('out', os.path.basename(pdf_file)),
            'watermark.pdf'
        )
        print(f'Обработано: {processed_pages} из {total_pages} страниц.\n')