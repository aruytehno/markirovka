# https://github.com/li0ard/nechestniy_znak/tree/main
import requests, urllib
from urllib.parse import quote_plus
import json
import os


class Lib:
    def __init__(self):
        pass

    def _get(self, content, type):
        return requests.get(f"https://mobile.api.crpt.ru/mobile/check?code={content}&codeType={type}").json()

    def infoFromDataMatrix(self, xyematrix):
        return self._get(xyematrix, "datamatrix")

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
        if str(jsonobject['codeFounded']) == 'True':
            if str(jsonobject['tiresData']['status']) == 'INTRODUCED':
                info_msg.append('В обороте ✅')
                info_msg.append(str(jsonobject['code']))
            elif str(jsonobject['tiresData']['status']) == 'RETIRED':
                info_msg.append('Выведен из оборота ❌')
                info_msg.append(str(jsonobject['code']))
            else:
                info_msg.append('Неизвестный статус кода ⚠️')
                info_msg.append(str(jsonobject['tiresData']['status']))
        else:
            info_msg.append('Код не найден ❌')
            info_msg.append(jsonobject['code'])

    except:
        info_msg.append('Ошибка получения данных')

    return info_msg


if __name__ == "__main__":
    with open('api_crpt' + os.sep + 'datamatrix.txt') as f:
        for code in f.read().splitlines():
            print(code)
            print(getInfoFromDataMatrix(code, "datamatrix"))
