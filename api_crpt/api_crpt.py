import requests, urllib
from urllib.parse import quote_plus
import json


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


def getInfoFromDataMatrix(self, content, type):
    '''
    https://stackoverflow.com/questions/37374165/parsing-json-using-try-and-except
    '''
    content = quote_plus(content)
    link = f"https://mobile.api.crpt.ru/mobile/check?code={content}&codeType={type}"
    requests_json = requests.get(link).json()
    input = json.dumps(requests_json)
    jsonobject = json.loads(input)
    info_msg = []
    try:
        if str(jsonobject['codeFounded']) == 'True':
            if jsonobject['tiresData'] != {}:
                if jsonobject['tiresData']['cisInfo'] != {}:
                    if str(jsonobject['tiresData']['cisInfo']['withdrawReason']) == 'OWN_USE':
                        info_msg.append('Не для продажи ❌')
                        info_msg.append('Код выведен из оборота')
                        info_msg.append(False)

                else:
                    info_msg.append('Товар проверен ✅')
                    info_msg.append(str(jsonobject['code']))
                    info_msg.append(True)
                info_msg.append(str(jsonobject['productName']))
        else:
            info_msg.append('Код не найден ❌')
            info_msg.append(jsonobject['code'])
    except:
        info_msg.append('Ошибка получения данных')

    return info_msg


if __name__ == "__main__":
    lib = Lib()
    with open('C:/Users/aruytehno/PycharmProjects/tires/test/datamatrix.txt') as f:
        lines = f.read().splitlines()
        print(lines)
        for code in lines:
            print(code)
            print(getInfoFromDataMatrix(code, "datamatrix"))

    # # code_info = json.getInfoFromDataMatrix("0104603720196471215wWbdE6v,f-sz", "datamatrix")
    # # code_info = json.getInfoFromDataMatrix("0104603720196457215bFNT4KLpJT3q", "datamatrix")
    # # code_info = json.getInfoFromDataMatrix("0104603720196471215b>CWR..DEE&8", "datamatrix")
    # code_info = json.getInfoFromDataMatrix("0104603720196396215TStuMCtP>K?N", "datamatrix")
    # print('code_info_in_test: ' + str(code_info))

    print(lib.infoFromEAN13(46494139))
    print(lib.infoFromDataMatrix("00000046209849Uon<TYfACyAJPHJ"))
    print(lib.infoFromQr("chek.markirovka.nalog.ru/kc/?kiz=RU-430302-AAA4050108"))
