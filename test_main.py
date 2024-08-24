import os
import unittest

from main import read_data
import os
import unittest
import glob

from main import get_files


class TestGetFiles(unittest.TestCase):
    def test_folder_exists_and_files_found(self):
        # Создаем папку с файлами
        input_folder = 'test_folder'
        file_type = '*.txt'
        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(os.path.join(input_folder, 'subfolder'), exist_ok=True)  # добавьте эту строку
        with open(os.path.join(input_folder, 'file1.txt'), 'w') as f:
            f.write('Hello, world!')
        with open(os.path.join(input_folder, 'subfolder', 'file2.txt'), 'w') as f:
            f.write('This is a test file.')
        os.makedirs(os.path.join(input_folder, 'subfolder'), exist_ok=True)

        # Тестируем метод get_files
        list_files = get_files(input_folder, file_type)
        self.assertIsInstance(list_files, list)
        self.assertEqual(len(list_files), 2)
        self.assertIn(os.path.join(input_folder, 'file1.txt'), list_files)
        self.assertIn(os.path.join(input_folder, 'subfolder', 'file2.txt'), list_files)

        # Удаляем папку и файлы
        os.remove(os.path.join(input_folder, 'file1.txt'))
        os.remove(os.path.join(input_folder, 'subfolder', 'file2.txt'))
        os.rmdir(os.path.join(input_folder, 'subfolder'))
        os.rmdir(input_folder)

    def test_folder_exists_and_no_files_found(self):
        # Создаем пустую папку
        input_folder = 'test_folder'
        file_type = '*.txt'
        os.makedirs(input_folder, exist_ok=True)

        # Тестируем метод get_files
        with self.assertRaises(SystemExit) as cm:
            get_files(input_folder, file_type)
        self.assertEqual(cm.exception.code, None)

        # Удаляем папку
        os.rmdir(input_folder)

    def test_folder_not_exists(self):
        # Тестируем метод get_files с несуществующей папкой
        input_folder = 'non_existent_folder'
        file_type = '*.txt'

        # Тестируем метод get_files
        with self.assertRaises(SystemExit) as cm:
            get_files(input_folder, file_type)
        self.assertEqual(cm.exception.code, None)

        # Проверяем, что папка была создана
        self.assertTrue(os.path.exists(input_folder))
        os.rmdir(input_folder)


if __name__ == '__main__':
    unittest.main()

class TestReadFile(unittest.TestCase):
    def test_file_exists_and_not_empty(self):
        # Создаем файл с содержимым
        file_path = 'test_file.txt'
        with open(file_path, 'w') as f:
            f.write('Hello, world!\n')
            f.write('This is a test file.\n')

        # Тестируем метод read_file
        lines = read_data(file_path)
        self.assertIsInstance(lines, list)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].strip(), 'Hello, world!')
        self.assertEqual(lines[1].strip(), 'This is a test file.')

        # Удаляем файл
        os.remove(file_path)

    def test_file_exists_and_empty(self):
        # Создаем пустой файл
        file_path = 'test_file.txt'
        with open(file_path, 'w') as f:
            pass

        # Тестируем метод read_file
        with self.assertRaises(SystemExit) as cm:
            read_data(file_path)
        self.assertEqual(cm.exception.code, None)

        # Удаляем файл
        os.remove(file_path)

    def test_file_not_exists(self):
        # Тестируем метод read_file с несуществующим файлом
        file_path = 'non_existent_file.txt'
        with self.assertRaises(SystemExit) as cm:
            read_data(file_path)
        self.assertEqual(cm.exception.code, None)

        # Проверяем, что файл был создан
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)


if __name__ == '__main__':
    unittest.main()