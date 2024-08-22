from fix_lines import fix_lines
import os


def create_folders(list_folders):
    for name_folder in list_folders:
        if not os.path.exists(name_folder):
            print('A folder has been created', name_folder)
            os.makedirs(name_folder)


if __name__ == "__main__":
    create_folders(['search', 'input', 'out'])

    fix_lines()  # input >>> out



