'''
Скрипт для замены двойных линий на одинарные в выгруженных файлах для удобства нарезки после печати.
'''

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
    put_watermark('input.pdf', 'output.pdf', 'watermark.pdf')
