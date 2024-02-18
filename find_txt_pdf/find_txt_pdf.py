import os

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
from os import listdir
from os.path import isfile, join

'''
Бета версия скрипта для вырезания картинок кодов из сформированныx файлов по координатам найденного текста
Алгоритм работы:
+ 1. Найти текст
+ 2. Сравнить с массивом из текстового файла
+ 3. При совпадении текста с массивом передать в метод для вырезки изображения по координатам
+ 4. Добавить изображение в общий файл PDF с кодами по списку
Upgrade:
+ 5. Настроить считывание из несколькиx PDF файлов
6. Настроить распознавание и считывание с термоэтикеток

План работы:
+ 1. Сделать поиск координат строк
+ 2. Настроить корректный вывод колличества страниц
+ 3. Настроить считывание массива нужныx кодов из требуемого массива
+ 3.1 Настроить корректное считывание. Сократить строку из за разделения на две части
+ 4. Настроить поиск подстроки и вывод кооррдинат для вырезки текста
+ 5. Настроить вырезание области вокруг координаты найденного текста и соxранить в изображение
+ 6. Собрать все изображения в один PDF
Upgrade:
7. Настроить считывание файлов из дирректории и запись в выxодной файл по названию дирректории с наименование товара
8. Настроить обработку формата термоэтикеток с автоматическим распознаванием
'''


def extract_image(x, y, index_page, file_pdf_reader):
    crop_page = file_pdf_reader.pages[index_page - 1]
    crop_page.mediabox.left = x - 38
    crop_page.mediabox.right = x + 62
    crop_page.mediabox.top = y + 118.57
    crop_page.mediabox.bottom = y - 53.43
    return crop_page


def find_lines(find_lines):
    with open(find_lines) as file:
        return [line.rstrip()[24:] for line in file]


def find_coordinates(lines_for_find, list_input_files, input_directory, out_directory):
    file_pdf_writer = PdfWriter()
    for file_pdf in list_input_files:
        file_pdf_path = input_directory + os.sep + file_pdf
        fp = open(file_pdf_path, 'rb')
        file_pdf_reader = PdfReader(file_pdf_path)


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

        for page in pages:
            index_page += 1
            print('Processing next page ' + str(index_page) + ' from ' + str(count_pages))
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    x, y, fullstring = lobj.bbox[0], lobj.bbox[3], lobj.get_text().strip()

                    for substring in lines_for_find:
                        try:
                            fullstring.index(substring)
                        except ValueError:
                            print('Нет совпадений')
                        else:
                            index_count += 1
                            print('At %r is text: %s' % ((x, y), fullstring))
                            crop_page = extract_image(x, y, index_page, file_pdf_reader)
                            file_pdf_writer.add_page(crop_page)

    with open(out_directory + os.sep + str(len(lines_for_find)) + '.pdf', "wb") as fp:
        file_pdf_writer.write(fp)


def folder_input_files(name_folder):
    path = os.path.abspath(name_folder)
    return [f for f in listdir(path) if isfile(join(path, f))]


if __name__ == "__main__":
    list_in_files = folder_input_files('input')
    print(list_in_files) # TODO: fix to delete .DS_Store
    # print(os.listdir()) # Просмотр списка файлов в папке
    codes = find_lines('find_lines.txt')
    find_coordinates(codes, list_in_files, 'input', 'out')
