import os
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

"""
Скрипт для проверки валидности кодов и получения их статусов через API ГИС МТ.
"""


def check_datamatrix(data_codes, code_type="datamatrix"):
    # Проверка каждого кода и вывод результатов
    for index, code in enumerate(data_codes, start=1):
        base_url = "https://mobile.api.crpt.ru/mobile/check"
        encoded_code = quote_plus(code)
        url = f"{base_url}?code={encoded_code}&codeType={code_type}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Ошибка при запросе: {e}")
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
        if len(data_codes) > 1:
            print(f"{index}/{len(data_codes)} {' '.join(info_msg)}")
        else:
            return info_msg

'''
Скрипт для поиска кодов в PDF-документе с общим массивом кодов после выгрузки, сохраняя найденные в новый PDF-файл.
'''


def find_codes(list_input_files, search_codes, target_folder, validate=False):
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
                            if validate:
                                i_out = ''
                                substring_list = [substring]
                                data_code = check_datamatrix(substring_list)
                                for i in data_code:
                                    i_out += i + ' '
                                name_file.append(data_code[2])
                                print(i_out + '\n')
                            else:
                                print(substring)

                            lines_not_found.remove(substring)
                        except ValueError:
                            pass
                        else:
                            index_count += 1
                            crop_page = file_pdf_reader.pages[index_page - 1]
                            crop_page.mediabox.left = x - 38
                            crop_page.mediabox.right = x + 62
                            crop_page.mediabox.top = y + 118.57
                            crop_page.mediabox.bottom = y - 53.43
                            file_pdf_writer.add_page(crop_page)

    if len(lines_not_found) == 0:
        print('\nВсе коды найдены')
    else:
        print('\nНе найденные коды: ' + str(len(lines_not_found)))
        for code_not_found in lines_not_found:
            print(code_not_found)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    if len(file_pdf_writer.pages) > 0:
        replace_values = {"/": "%", "[": "", "]": "", "\'": "", "\"": ""}
        name = str(list(set(name_file))) + ' (' + str(len(search_codes)) + ' pcs).pdf'
        for i, j in replace_values.items():
            name = name.replace(i, j)
        with open(target_folder + os.sep + name, "wb") as fp:
            file_pdf_writer.write(fp)


'''
Скрипт для фикса линий в PDF-файлах.
'''


def fix_lines(list_pdf_files, target_folder, watermark_pdf_path):
    # Обрабатываем каждый файл
    for pdf_file in list_pdf_files:
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
            print(f'Обработано: {i} из {total_pages} страниц в файле {pdf_file}.')

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        with open(os.path.join(target_folder, os.path.basename(pdf_file)), 'wb') as out_file:
            pdf_writer.write(out_file)


def read_data(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            if not lines:
                print(f"Файл '{file_path}' пустой.")
                exit()
            return lines
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            pass
        print(f"Отсутствующий файл '{file_path}' создан")
        exit()


def get_files(input_folder, file_type):
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f'Отсутствующая папка "{input_folder}" была создана')
        exit()
    # Получаем список всех файлов с указанным типом из всех вложенных директорий
    list_files = [f for f in glob.glob(os.path.join(input_folder, '**', file_type), recursive=True)]

    # Если файлов нет, выводим сообщение и останавливаем программу
    if not list_files:
        print(f"В папке '{input_folder}' и ее вложенных директориях нет файлов с типом '{file_type}'.")
        exit()
    return list_files


if __name__ == "__main__":
    # datamatrix.txt >>> API
    check_datamatrix(read_data('datamatrix.txt'))
    # search  >>> datamatrix.txt >>> out
    find_codes(get_files('input', '*.pdf'), read_data('datamatrix.txt'), 'out', True)
    # input >>> out
    fix_lines(get_files('input', '*.pdf'), 'out', 'watermark.pdf')
