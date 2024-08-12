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


if __name__ == "__main__":
    checker = CodeChecker()

    # Чтение кодов из файла
    with open('datamatrix.txt') as f:
        data_codes = f.read().splitlines()

    # Проверка каждого кода и вывод результатов
    for index, code in enumerate(data_codes, start=1):
        info = checker.get_info(code)
        print(f"{index}/{len(data_codes)} {' '.join(info)}")
