import os
import unittest
from config import DATAMATRIX_FILE, RESULTS_FOLDER
from core.code_service import CodeService
from utils.file_utils import clear_directory, save_validation_report, format_validation_results


class TestCodeService(unittest.TestCase):

    def setUp(self):
        clear_directory(RESULTS_FOLDER)
        with open(DATAMATRIX_FILE, 'r') as f:
            self.codes = [line.strip() for line in f if line.strip()][:5]  # Берем первые 5 кодов для теста
        self.code_service = CodeService()

    def test_get_api_data(self):
        """Тестируем получение данных по кодам через API"""
        results = self.code_service.get_api_data(self.codes)

        # Сохраняем отчет
        save_validation_report(results)

        # Проверки
        self.assertIsInstance(results, list)
        for item in results:
            self.assertIsInstance(item, dict)  # Предполагаем, что каждый результат — dict

        # Дополнительно можно вывести форматированный результат (для отладки)
        formatted = format_validation_results(results)
        self.assertIsInstance(formatted, str)

    def test_get_pdf_with_codes(self):
        """Тестируем сохранение PDF-файлов по кодам"""
        results = self.code_service.get_pdf_with_codes(self.codes)

        # Проверки структуры результатов
        self.assertIsInstance(results, list)
        for count, product_name, pdf_bytes in results:
            self.assertIsInstance(count, int)
            self.assertIsInstance(product_name, str)
            self.assertIsInstance(pdf_bytes, bytes)

            # Сохраняем файл
            filename = f"({count})_{product_name}.pdf"
            filepath = os.path.join(RESULTS_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)

            # Проверяем, что файл действительно сохранился
            self.assertTrue(os.path.exists(filepath))
            self.assertGreater(os.path.getsize(filepath), 0)


if __name__ == "__main__":
    unittest.main()
