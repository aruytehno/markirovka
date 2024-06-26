'''
Скрипт предназначен для поиска требуемых кодов в pdf документе с общим массивом кодов после выгрузки,
сохраняя вырезанные в новый pdf файл.
'''
import glob
import logging
import os
import sys

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


def find_coordinates(search_codes, list_input_files, target_folder):
    name_file = []
    lines_not_found = search_codes.copy()
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

                    for substring in search_codes:
                        try:
                            fullstring.index(substring[24:])
                            print('\nНайдено совпадение: ' + substring[24:])
                            info_code = print_data_code(substring)
                            name_file.append(info_code[1])
                            print(info_code[0])
                            lines_not_found.remove(substring)
                        except ValueError:
                            logging.info('Нет совпадений')
                        else:
                            index_count += 1
                            # print('At %r is text: %s' % ((x, y), fullstring))
                            crop_page = extract_image(x, y, index_page, file_pdf_reader)
                            file_pdf_writer.add_page(crop_page)

    if len(lines_not_found) == 0:
        print('\nВсе коды найдены')
    else:
        print('\nНе найденные коды: ' + str(len(lines_not_found)))
        for code_not_found in lines_not_found:
            print(code_not_found)

    if len(file_pdf_writer.pages) > 0:
        with open(target_folder + os.sep + print_name_file(name_file, search_codes), "wb") as fp:
            file_pdf_writer.write(fp)


def print_data_code(substring):
    i_out = ''
    data_code = getInfoFromDataMatrix(substring, "datamatrix")
    for i in data_code:
        i_out += i + ' '
    return [i_out + '\n', data_code[2]]


def print_name_file(name_file, lines):
    replace_values = {"/": "%", "[": "", "]": "", "\'": "", "\"": ""}
    name = str(list(set(name_file))) + ' (' + str(len(lines)) + ' pcs).pdf'
    return multiple_replace(name, replace_values)


def multiple_replace(target_str, replace_values):
    for i, j in replace_values.items():
        target_str = target_str.replace(i, j)
    return target_str


if __name__ == "__main__":
    list_folders = ['input', 'out']
    for folder in list_folders:
        if not os.path.exists(folder):
            print('Создана папка', folder)
            os.makedirs(folder)

    list_input = glob.glob('input' + os.sep + '*.pdf')

    if os.path.isfile('find_lines.txt'):
        with open('find_lines.txt', 'r') as file:
            codes_for_search = [line.rstrip() for line in file]
    else:
        print('Создан файл find_lines.txt')
        with open('find_lines.txt', 'w') as file:
            pass
        sys.exit()

    if len(codes_for_search) == 0:
        print('В файле \'find_lines.txt\' нет кодов для поиска')
        sys.exit()

    if len(list_input) == 0:
        print('В папке \'input\' нет файлов для обработки')
        sys.exit()

    find_coordinates(codes_for_search, list_input, 'out')
