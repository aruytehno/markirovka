'''
Скрипт предназначен для поиска требуемых кодов в pdf документе с общим массивом кодов после выгрузки, сохраняя вырезанные в новый pdf файл.
'''
import glob
import logging
import os
from pathlib import Path

from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
# count pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
# extract image
from PyPDF2 import PdfWriter, PdfReader
# folder

from api_crpt.api_crpt import getInfoFromDataMatrix


def extract_image(x, y, index_page, file_pdf_reader):
    crop_page = file_pdf_reader.pages[index_page - 1]
    crop_page.mediabox.left = x - 38
    crop_page.mediabox.right = x + 62
    crop_page.mediabox.top = y + 118.57
    crop_page.mediabox.bottom = y - 53.43
    return crop_page


def find_coordinates(list_to_search, list_input_files, target_folder):
    name_file = []
    with open(list_to_search) as file:
        lines = [line.rstrip() for line in file]

    file_pdf_writer = PdfWriter()
    for file_pdf in list_input_files:
        fp = open(file_pdf, 'rb')
        file_pdf_reader = PdfReader(file_pdf)

        # This will give you the count of pages
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        count_pages = resolve1(document.catalog['Pages'])['Count']

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        index_page = 0
        index_count = 0

        print('Поиск в файле: ' + file_pdf)
        for page in pages:
            index_page += 1
            print('Обработано страниц ' + str(index_page) + ' из ' + str(count_pages) + ' в файле ' + file_pdf)
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    x, y, fullstring = lobj.bbox[0], lobj.bbox[3], lobj.get_text().strip()

                    for substring in lines:
                        try:
                            fullstring.index(substring[24:])
                            print('\nНайдено совпадение: ' + substring[24:])

                            i_out = ''
                            data_code = getInfoFromDataMatrix(substring, "datamatrix")
                            print(data_code)
                            name_file.append(data_code[2])
                            print(name_file)
                            for i in data_code:
                                i_out += i + ' '
                            print(i_out + '\n')
                        except ValueError:
                            logging.info('Нет совпадений')
                        else:
                            index_count += 1
                            # print('At %r is text: %s' % ((x, y), fullstring))
                            crop_page = extract_image(x, y, index_page, file_pdf_reader)
                            file_pdf_writer.add_page(crop_page)

    replace_values = {"/": "%", "[": "", "]": "", "\'": "", "\"": ""}
    name = str(list(set(name_file))) + ' (' + str(len(lines)) + ' pcs).pdf'
    name = multiple_replace(name, replace_values)
    Path(target_folder).mkdir(parents=True, exist_ok=True)
    with open(target_folder + os.sep + name, "wb") as fp:
        file_pdf_writer.write(fp)


def multiple_replace(target_str, replace_values):
    for i, j in replace_values.items():
        target_str = target_str.replace(i, j)
    return target_str


if __name__ == "__main__":
    find_coordinates('find_lines.txt', glob.glob("*.pdf"), "out")
