import os
import unittest
from main import get_files, read_data


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.input_folder = 'test_folder'
        self.file_type = '*.txt'
        os.makedirs(self.input_folder, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.input_folder):
            for root, dirs, files in os.walk(self.input_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.input_folder)


class TestGetFiles(BaseTestCase):
    def test_folder_exists_and_files_found(self):
        os.makedirs(os.path.join(self.input_folder, 'subfolder'), exist_ok=True)
        with open(os.path.join(self.input_folder, 'file1.txt'), 'w') as f:
            f.write('Hello, world!')
        with open(os.path.join(self.input_folder, 'subfolder', 'file2.txt'), 'w') as f:
            f.write('This is a test file.')

        list_files = get_files(self.input_folder, self.file_type)
        self.assertIsInstance(list_files, list)
        self.assertEqual(len(list_files), 2)
        self.assertIn(os.path.join(self.input_folder, 'file1.txt'), list_files)
        self.assertIn(os.path.join(self.input_folder, 'subfolder', 'file2.txt'), list_files)

    def test_folder_exists_and_no_files_found(self):
        with self.assertRaises(SystemExit) as cm:
            get_files(self.input_folder, self.file_type)
        self.assertEqual(cm.exception.code, None)

    def test_folder_not_exists(self):
        os.rmdir(self.input_folder)
        with self.assertRaises(SystemExit) as cm:
            get_files(self.input_folder, self.file_type)
        self.assertEqual(cm.exception.code, None)
        self.assertTrue(os.path.exists(self.input_folder))


class TestReadFile(unittest.TestCase):
    def setUp(self):
        self.file_path = 'test_file.txt'

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_file_exists_and_not_empty(self):
        with open(self.file_path, 'w') as f:
            f.write('Hello, world!\n')
            f.write('This is a test file.\n')

        lines = read_data(self.file_path)
        self.assertIsInstance(lines, list)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].strip(), 'Hello, world!')
        self.assertEqual(lines[1].strip(), 'This is a test file.')

    def test_file_exists_and_empty(self):
        with open(self.file_path, 'w') as f:
            pass

        with self.assertRaises(SystemExit) as cm:
            read_data(self.file_path)
        self.assertEqual(cm.exception.code, None)

    def test_file_not_exists(self):
        with self.assertRaises(SystemExit) as cm:
            read_data(self.file_path)
        self.assertEqual(cm.exception.code, None)
        self.assertTrue(os.path.exists(self.file_path))


if __name__ == '__main__':
    unittest.main()
