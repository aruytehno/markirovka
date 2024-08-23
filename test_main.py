import os
import unittest

from main import read_file


class TestReadFile(unittest.TestCase):
    def test_file_exists_and_not_empty(self):
        # Создаем файл с содержимым
        file_path = 'test_file.txt'
        with open(file_path, 'w') as f:
            f.write('Hello, world!\n')
            f.write('This is a test file.\n')

        # Тестируем метод read_file
        lines = read_file(file_path)
        self.assertIsNotNone(lines)
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
        with self.assertRaises(SystemExit):
            read_file(file_path)

        # Удаляем файл
        os.remove(file_path)

    def test_file_not_exists(self):
        # Тестируем метод read_file с несуществующим файлом
        file_path = 'non_existent_file.txt'
        with self.assertRaises(SystemExit):
            read_file(file_path)

        # Проверяем, что файл был создан
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)


if __name__ == '__main__':
    unittest.main()