import unittest
import tempfile
import os
from utils.file_utils import get_available_products

class TestGetAvailableProducts(unittest.TestCase):

    def setUp(self):
        # Создаем временную директорию
        self.test_dir = tempfile.TemporaryDirectory()
        self.path = self.test_dir.name

    def tearDown(self):
        # Удаляем временную директорию
        self.test_dir.cleanup()

    def test_get_available_products(self):
        # Создаем подпапки
        folder1 = os.path.join(self.path, "folder1")
        folder2 = os.path.join(self.path, "folder2")
        os.makedirs(folder1)
        os.makedirs(folder2)
        # Создаем файл
        with open(os.path.join(self.path, "file.txt"), "w") as f:
            f.write("test")

        result = get_available_products(self.path)
        self.assertEqual(set(result), {"folder1", "folder2"})
        self.assertNotIn("file.txt", result)

    def test_get_available_products_nonexistent_folder(self):
        result = get_available_products("/nonexistent/path")
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
