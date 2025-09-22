import requests
from urllib.parse import quote_plus
from typing import List
from datetime import datetime, timedelta
from logger_config import logger

STATUS_MAP = {
    'INTRODUCED': 'В обороте ✅',
    'RETIRED': 'Выбыл из оборота ❌',
    'EMITTED': 'Эмитирован, выпущен ✔️',
    'APPLIED': 'Эмитирован, получен 🔗',
    'WRITTEN_OFF': 'КИ списан 🟥',
    'DISAGGREGATION': 'Расформирован (упаковка) 📦🟥'
}

HEADERS = {
    "accept": "application/json",
    "user-agent": "Platform: iOS 17.2; AppVersion: 4.47.0; Device: iPhone 14 Pro;",
    "client": "iOS 17.2; AppVersion: 4.47.0; Device: iPhone 14 Pro;"
}


def detect_code_type(code: str) -> str:
    """Простейшее определение типа кода"""
    if code.isdigit() and len(code) == 13:
        return "ean13"
    if code.startswith("http"):
        return "qr"
    return "datamatrix"


def check_code(code: str, db) -> dict:
    """Проверка кода через API с кэшированием в БД"""
    logger.debug(f"Начало проверки кода: {code}")

    # Проверяем в БД
    cached_result = db.get_code_info(code)

    if cached_result:
        last_updated_str = cached_result.get('updated_at') or cached_result.get('created_at')

        # Преобразуем строку в datetime объект
        if isinstance(last_updated_str, str):
            # Убираем миллисекунды если есть
            if '.' in last_updated_str:
                last_updated_str = last_updated_str.split('.')[0]

            # Парсим дату
            try:
                last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    last_updated = datetime.strptime(last_updated_str, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    # Если не получается распарсить, считаем данные устаревшими
                    logger.warning(f"Не удалось распарсить дату для кода {code}: {last_updated_str}")
                    last_updated = datetime.min
        else:
            last_updated = datetime.min

        # Если прошло менее 10 минут с последнего обновления ИЛИ создания
        if datetime.now() - last_updated < timedelta(minutes=10):
            logger.info(f"📦 Данные из БД (актуальные): {code}")
            return cached_result
        else:
            logger.info(f"🔄 Данные устарели, запрашиваем API: {code}")

    # Если кода нет в БД или данные устарели - запрашиваем API
    base_url = "https://mobile.api.crpt.ru/mobile/check"
    encoded_code = quote_plus(code)
    code_type = detect_code_type(code)
    url = f"{base_url}?code={encoded_code}&codeType={code_type}"

    logger.debug(f"Запрос к API: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"Ответ API для кода {code}: {data}")

    except requests.exceptions.Timeout:
        error_msg = f"Timeout error при проверке кода {code}"
        logger.error(error_msg)
        result = {"code": code, "error": "Timeout error", "found": False}

    except requests.exceptions.ConnectionError:
        error_msg = f"Connection error при проверке кода {code}"
        logger.error(error_msg)
        result = {"code": code, "error": "Connection error", "found": False}

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error при проверке кода {code}: {e}"
        logger.error(error_msg)
        result = {"code": code, "error": f"HTTP error: {e}", "found": False}

    except Exception as e:
        error_msg = f"Неожиданная ошибка при проверке кода {code}: {e}"
        logger.error(error_msg, exc_info=True)
        result = {"code": code, "error": str(e), "found": False}

    else:
        result = {"code": code, "found": data.get("codeFounded", False)}
        if result["found"]:
            status = data.get("tiresData", {}).get("status")
            result["status"] = status
            result["status_text"] = STATUS_MAP.get(status, f"Неизвестный статус ⚠️ [{status}]")
            result["product_name"] = data.get("productName", "Неизвестный продукт")

            logger.info(f"Код {code} найден. Статус: {result['status_text']}, Продукт: {result['product_name']}")
        else:
            result["status_text"] = "Код не найден ❗"
            logger.warning(f"Код {code} не найден в системе")

    # Сохраняем результат в БД
    try:
        db.save_check_result(result)
        logger.debug(f"Результат проверки кода {code} сохранен в БД")
    except Exception as e:
        logger.error(f"Ошибка при сохранении результата в БД для кода {code}: {e}")

    return result


def check_codes_from_list(codes: List[str]) -> List[dict]:
    """Проверка списка кодов"""
    from infrastructure.database import MarkingCodeDB

    db = MarkingCodeDB()
    logger.info(f"Начало проверки списка из {len(codes)} кодов")
    results = []

    for i, code in enumerate(codes, 1):
        logger.debug(f"Проверка кода {i}/{len(codes)}: {code}")
        try:
            result = check_code(code, db)
            results.append(result)
        except Exception as e:
            error_msg = f"Ошибка при проверке кода {code}: {e}"
            logger.error(error_msg, exc_info=True)
            results.append({"code": code, "error": str(e), "found": False})

    logger.info(f"Завершена проверка списка из {len(codes)} кодов")
    return results