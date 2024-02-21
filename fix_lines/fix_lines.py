'''
Скрипт для замены двойных линий на одинарные в выгруженных файлах для удобства нарезки после печати.
'''
import os

from PyPDF2 import PdfReader, PdfWriter

def put_watermark(input_pdf, output_pdf, watermark):
    watermark_instance = PdfReader(watermark)
    watermark_page = watermark_instance.pages[0]
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    for page in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as out:
        pdf_writer.write(out)


if __name__ == "__main__":
    list_files = os.listdir()
    print(list_files)
    list_files.remove('fix_lines.py')
    list_files.remove('watermark.pdf')
    print(list_files)
    for file in list_files:
        print(file)
        put_watermark(file, file.replace('.pdf', '_fix_lines.pdf'), 'watermark.pdf')
