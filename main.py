from config import DATAMATRIX_FILE, RESULTS_FOLDER
from core.code_service import CodeService
from core.code_manager import FreeCodeManager
from utils.file_utils import clear_directory
import os

def validate():
    """Тестируем получение данных по кодам через API"""
    clear_directory(RESULTS_FOLDER)

    with open(DATAMATRIX_FILE, 'r') as f:
        codes = [line.strip() for line in f if line.strip()]

    code_service = CodeService()
    results = code_service.get_api_data(codes)

    from utils.file_utils import save_validation_report
    save_validation_report(results)  # Сохранит отчет в файл

    # Дополнительно можно вывести в консоль
    from utils.file_utils import format_validation_results
    print(format_validation_results(results))


def extract():
    """Извлечь коды из PDF"""
    clear_directory(RESULTS_FOLDER)

    with open(DATAMATRIX_FILE, 'r') as f:
        codes = [line.strip() for line in f if line.strip()]

    code_service = CodeService()
    results_api_data = code_service.get_api_data(codes)

    from utils.file_utils import save_validation_report
    save_validation_report(results_api_data)  # Сохранит отчет в .txt файл

    results_pdf_with_codes = code_service.get_pdf_with_codes(codes)


    for count, product_name, pdf_bytes in results_pdf_with_codes:
        filename = f"({count})_{product_name}.pdf"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes) # Сохранит результат в .pdf файл

    # Дополнительно вывести в консоль
    from utils.file_utils import format_validation_results
    print(format_validation_results(results_api_data))


def available():
    """Получить свободные коды"""
    clear_directory(RESULTS_FOLDER)

    free = FreeCodeManager()

    # Получаем список доступных товаров
    products = free.get_available_products()

    if not products:
        print("❌ Нет доступных товаров для тестирования")
        return

    # Выводим нумерованный список товаров
    print("📦 Доступные товары:")
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product}")

    # Выбор товара
    try:
        choice = int(input("\nВведите номер товара: "))
        if choice < 1 or choice > len(products):
            print("❌ Неверный номер товара")
            return
        product_name = products[choice - 1]
    except ValueError:
        print("❌ Введите число")
        return

    # Ввод количества кодов
    try:
        quantity = int(input("Введите количество кодов: "))
        if quantity <= 0:
            print("❌ Количество должно быть положительным")
            return
    except ValueError:
        print("❌ Введите число")
        return

    print(f"\n🔍 Тестируем товар: {product_name}")
    print(f"📊 Запрашиваем кодов: {quantity}")

    # Получаем свободные коды
    free_codes = free.get_free_codes(product_name, quantity)

    print(f"\n✅ Результат:")
    print(free_codes)
    print(f"Запрошено: {quantity} кодов")
    print(f"Получено: {len(free_codes)} кодов")

    if free_codes:
        print("🎯 Полученные коды:")
        for i, code in enumerate(free_codes, 1):
            print(f"  {i}. {code}")
    else:
        print("❌ Не удалось получить свободные коды")

    code_service = CodeService()
    results_api_data = code_service.get_api_data(free_codes)

    from utils.file_utils import save_validation_report
    save_validation_report(results_api_data)  # Сохранит отчет в .txt файл

    results_pdf_with_codes = code_service.get_pdf_with_codes(free_codes)


    for count, product_name, pdf_bytes in results_pdf_with_codes:
        filename = f"({count})_{product_name}.pdf"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes) # Сохранит результат в .pdf файл

    # Дополнительно вывести в консоль
    from utils.file_utils import format_validation_results
    print(format_validation_results(results_api_data))


def show_menu():
        """Показать меню выбора режима"""
        menu_text = """
🎯 Markirovka - Система работы с кодами маркировки
==================================================
1. 🔍 Проверка кодов через API
2. 📄 Извлечение кодов из PDF
3. 📦 Получение свободных кодов
0. ❌ Выход
==================================================
"""
        print(menu_text)


if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("Выберите действие (0-3): ").strip()

        if choice == "0":
            print("👋 До свидания!")
            break
        elif choice == "1":
            validate()
        elif choice == "2":
            extract()
        elif choice == "3":
            available()
        else:
            print("❌ Неверный выбор. Введите число от 0 до 3")
            continue

        input("\n⏎ Нажмите Enter для возврата в меню...")
