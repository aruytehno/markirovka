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
import requests
from urllib.parse import quote_plus

class CodeChecker:
    BASE_URL = "https://mobile.api.crpt.ru/mobile/check"

    def __init__(self):
        pass

    def _get_info(self, code, code_type):
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

if __name__ == "__main__":
    checker = CodeChecker()

    with open('datamatrix.txt') as f:
        data_codes = f.read().splitlines()

    for index, code in enumerate(data_codes, start=1):
        info = checker.get_info(code)
        print(f"{index}/{len(data_codes)} {' '.join(info)}")
