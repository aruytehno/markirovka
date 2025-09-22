from config import RESULTS_FOLDER
from utils.file_utils import clear_directory
import unittest
from core.code_manager import FreeCodeManager


class TestCodeManager(unittest.TestCase):
    def test_get_available_products(self):
        free = FreeCodeManager()
        products = free.get_available_products()
        self.assertIsInstance(products, list)
        print(products)

    def test_get_free_codes(self):
        """Тестируем получение свободных кодов для товара"""
        clear_directory(RESULTS_FOLDER)

        free = FreeCodeManager()

        # Получаем список доступных товаров
        products = free.get_available_products()
        print("Доступные товары:", products)

        if not products:
            self.skipTest("Нет доступных товаров для тестирования")

        # Выбираем первый товар для теста
        product_name = products[0]
        quantity = 3  # Запрашиваем 3 кода для теста

        print(f"\nТестируем товар: {product_name}")
        print(f"Запрашиваем кодов: {quantity}")

        # Получаем свободные коды
        free_codes = free.get_free_codes(product_name, quantity)

        print(f"\nРезультат:")
        print(f"Запрошено: {quantity} кодов")
        print(f"Получено: {len(free_codes)} кодов")
        print("Коды:", free_codes)

        # Проверки
        self.assertIsInstance(free_codes, list)
        self.assertTrue(all(isinstance(code, str) for code in free_codes))
        self.assertLessEqual(len(free_codes), quantity)

if __name__ == "__main__":
    unittest.main()