import os
import sys
import glob

from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from PyPDF2 import PdfWriter, PdfReader
import requests
from urllib.parse import quote_plus


class CodeChecker:
    """
    Класс для проверки валидности кодов и получения их статусов через API ГИС МТ.

    Атрибуты:
    - BASE_URL: Базовый URL для запросов к API.

    Методы:
    - get_info: Получает информацию о коде, проверяя его по типу.
    - _get_info: Внутренний метод для отправки запроса и получения данных.
    """

    BASE_URL = "https://mobile.api.crpt.ru/mobile/check"

    def _get_info(self, code, code_type):
        """
        Отправляет запрос к API для получения информации о коде.

        :param code: Код для проверки (например, DataMatrix, EAN13).
        :param code_type: Тип кода ('datamatrix', 'ean13', 'qr').
        :return: JSON ответ от API или None в случае ошибки.
        """
        encoded_code = quote_plus(code)
        url = f"{self.BASE_URL}?code={encoded_code}&codeType={code_type}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def get_info(self, code, code_type="datamatrix"):
        """
        Получает информацию о коде и возвращает статус и данные о продукте.

        :param code: Код для проверки.
        :param code_type: Тип кода ('datamatrix', 'ean13', 'qr').
        :return: Список сообщений о статусе и продукте.
        """
        data = self._get_info(code, code_type)
        if not data:
            return ["Ошибка получения данных 🛑"]

        info_msg = [data.get('code', 'Неизвестный код')]

        if data.get('codeFounded'):
            status = data.get('tiresData', {}).get('status', 'Неизвестный статус')
            status_messages = {
                'INTRODUCED': 'В обороте ✅',
                'RETIRED': 'Выбыл из оборота ❌',
                'EMITTED': 'Эмитирован, выпущен ✔️',
                'APPLIED': 'Эмитирован, получен 🔗',
                'WRITTEN_OFF': 'КИ списан 🟥',
                'DISAGGREGATION': 'Расформирован (только для упаковок) 📦🟥'
            }
            info_msg.append(status_messages.get(status, f'Неизвестный статус кода ⚠️ [{status}]'))
            product_name = data.get('productName', 'Неизвестный продукт')
            info_msg.append(f'[{product_name}]')
        else:
            info_msg.append('Код не найден ❗')

        return info_msg


def check_datamatrix():
    checker = CodeChecker()

    if os.path.isfile('api_crpt/datamatrix.txt'):
        with open('api_crpt/datamatrix.txt', 'r') as file:
            codes_for_search = [line.rstrip() for line in file]
    else:
        print('Создан файл datamatrix.txt')
        with open('api_crpt/datamatrix.txt', 'w') as file:
            pass
        sys.exit()

    # Чтение кодов из файла
    with open('api_crpt/datamatrix.txt') as f:
        data_codes = f.read().splitlines()

    # Проверка каждого кода и вывод результатов
    for index, code in enumerate(data_codes, start=1):
        info = checker.get_info(code)
        print(f"{index}/{len(data_codes)} {' '.join(info)}")




'''
Скрипт предназначен для поиска требуемых кодов в PDF-документе с общим массивом кодов после выгрузки,
сохраняя вырезанные в новый PDF-файл.
'''


def extract_image(x, y, index_page, file_pdf_reader):
    """
    Извлекает обрезанную часть страницы PDF на основе координат и индекса страницы.

    :param x: Координата X центра области для обрезки (float).
    :param y: Координата Y центра области для обрезки (float).
    :param index_page: Индекс страницы для обработки (int).
    :param file_pdf_reader: Объект PdfReader для чтения страниц PDF.
    :return: Обрезанную страницу в формате PdfReader.
    """
    crop_page = file_pdf_reader.pages[index_page - 1]
    crop_page.mediabox.left = x - 38
    crop_page.mediabox.right = x + 62
    crop_page.mediabox.top = y + 118.57
    crop_page.mediabox.bottom = y - 53.43
    return crop_page


def find_coordinates(search_codes, list_input_files, target_folder):
    """
    Ищет указанные коды в списке PDF-документов и сохраняет вырезанные страницы с найденными кодами в новый PDF-файл.

    :param search_codes: Список кодов для поиска (list).
    :param list_input_files: Список путей к входным PDF-файлам (list).
    :param target_folder: Папка для сохранения результата (str).
    :return: None
    """
    name_file = []
    lines_not_found = search_codes.copy()
    file_pdf_writer = PdfWriter()

    for file_pdf in list_input_files:
        fp = open(file_pdf, 'rb')
        file_pdf_reader = PdfReader(file_pdf)

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
                            pass
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
    """
    Получает информацию о коде и возвращает отформатированные данные.

    :param substring: Код для проверки (str).
    :return: Список с отформатированной информацией о коде и именем файла (list).
    """
    i_out = ''
    code_checker = CodeChecker()
    data_code = code_checker.get_info(substring, "datamatrix")
    for i in data_code:
        i_out += i + ' '
    return [i_out + '\n', data_code[2]]


def print_name_file(name_file, lines):
    """
    Форматирует имя файла для сохранения, заменяя нежелательные символы.

    :param name_file: Список имен файлов (list).
    :param lines: Список не найденных кодов (list).
    :return: Отформатированное имя файла (str).
    """
    replace_values = {"/": "%", "[": "", "]": "", "\'": "", "\"": ""}
    name = str(list(set(name_file))) + ' (' + str(len(lines)) + ' pcs).pdf'
    return multiple_replace(name, replace_values)


def multiple_replace(target_str, replace_values):
    """
    Заменяет все вхождения подстрок в строке на заданные значения.

    :param target_str: Целевая строка (str).
    :param replace_values: Словарь замен, где ключи - это подстроки для замены, а значения - это заменяющие строки (dict).
    :return: Измененную строку (str).
    """
    for i, j in replace_values.items():
        target_str = target_str.replace(i, j)
    return target_str


def find_txt_pdf():
    """
    Основной блок кода выполняется при запуске скрипта как основной программы.
    Создаются необходимые папки, считываются пути к входным PDF-файлам и коды для поиска,
    и вызывается функция find_coordinates для поиска кодов и сохранения результатов.
    """
    list_folders = ['input', 'out']
    for folder in list_folders:
        if not os.path.exists(folder):
            print('Создана папка', folder)
            os.makedirs(folder)

    list_input = glob.glob('input' + os.sep + '*.pdf')

    if os.path.isfile('find_txt_pdf/find_lines.txt'):
        with open('find_txt_pdf/find_lines.txt', 'r') as file:
            codes_for_search = [line.rstrip() for line in file]
    else:
        print('Создан файл find_lines.txt')
        with open('find_txt_pdf/find_lines.txt', 'w') as file:
            pass
        sys.exit()

    if len(codes_for_search) == 0:
        print('В файле \'find_lines.txt\' нет кодов для поиска')
        sys.exit()

    if len(list_input) == 0:
        print('В папке \'input\' нет файлов для обработки')
        sys.exit()

    find_coordinates(codes_for_search, list_input, 'out')





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


def create_folders(list_folders):
    for name_folder in list_folders:
        if not os.path.exists(name_folder):
            print('A folder has been created', name_folder)
            os.makedirs(name_folder)


if __name__ == "__main__":
    create_folders(['search', 'input', 'out'])
    fix_lines('input', 'out', 'watermark.pdf', '*.pdf')  # input >>> out
    find_txt_pdf()
    check_datamatrix()
