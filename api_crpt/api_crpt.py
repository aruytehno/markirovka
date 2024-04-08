# https://github.com/li0ard/nechestniy_znak/tree/main
import requests
from urllib.parse import quote_plus
import json

'''
Скрипт для проверки валидности кодов - находятся ли они в обороте или нет.

Описание API ГИС МТ
https://znak-it.ru/wp-content/uploads/2022/04/api-gis-mt.pdf

Статус товара/КИ:
EMITTED – Эмитирован. Выпущен;
APPLIED – Эмитирован. Получен;
INTRODUCED – В обороте;
WRITTEN_OFF – КИ списан;
RETIRED – Выбыл;
DISAGGREGATION – Расформирован (только для упаковок)
'''
class Lib:
    def __init__(self):
        pass

    def _get(self, content, type):
        return requests.get(f"https://mobile.api.crpt.ru/mobile/check?code={content}&codeType={type}").json()

    def infoFromDataMatrix(self, datamatrix):
        return self._get(datamatrix, "datamatrix")

    def infoFromEAN13(self, ean13):
        return self._get(ean13, "ean13")

    def infoFromQr(self, qr):
        return self._get(qr, "qr")

def getInfoFromDataMatrix(content, type):
    content = quote_plus(content)  # для кодирования символов при передаче AP
    link = f"https://mobile.api.crpt.ru/mobile/check?code={content}&codeType={type}"
    requests_json = requests.get(link).json()
    input = json.dumps(requests_json)
    jsonobject = json.loads(input)
    info_msg = []

    try:
        info_msg.append(jsonobject['code'])
        if str(jsonobject['codeFounded']) == 'True':
            if str(jsonobject['tiresData']['status']) == 'INTRODUCED':
                info_msg.append('В обороте ✅')
            elif str(jsonobject['tiresData']['status']) == 'RETIRED':
                info_msg.append('Выбыл из оборота ❌')
            elif str(jsonobject['tiresData']['status']) == 'EMITTED':
                info_msg.append('Эмитирован, выпущен ✔️')
            elif str(jsonobject['tiresData']['status']) == 'APPLIED':
                info_msg.append('Эмитирован, получен 🔗')
            elif str(jsonobject['tiresData']['status']) == 'WRITTEN_OFF':
                info_msg.append('КИ списан 🟥')
            elif str(jsonobject['tiresData']['status']) == 'DISAGGREGATION':
                info_msg.append('Расформирован (только для упаковок) 📦🟥')
            else:
                info_msg.append('Неизвестный статус кода ⚠️')
                info_msg.append('[' + str(jsonobject['tiresData']['status']) + ']')
            info_msg.append('[' + str(jsonobject['productName']) + ']')
        else:
            info_msg.append('Код не найден ❗')

    except:
        info_msg.append('Ошибка получения данных 🛑')

    return info_msg


if __name__ == "__main__":
    with open('datamatrix.txt') as f:
        counter = 0
        data_codes = f.read().splitlines()
        len_data_codes = len(data_codes)

        for code in data_codes:
            counter += 1
            i_out = ''
            for info_data in getInfoFromDataMatrix(code, "datamatrix"):
                i_out += info_data + ' '
            print(str(counter) + '/' + str(len_data_codes) + ' ' + i_out)
