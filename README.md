---

# Markirovka
###### на основе https://github.com/li0ard/nechestniy_znak/tree/main
Проект включает в себя набор скриптов для работы с системой {"Честный знак"](https://честныйзнак.рф/), предназначенных для проверки кодов, обработки PDF-документов и подготовки их к печати.

## Скрипты

- **`api_crpt.py`**  
  Скрипт для проверки валидности кодов. Позволяет определить, находятся ли коды в обороте, а также получить информацию о их статусах.

- **`find_txt_pdf.py`**  
  Скрипт для поиска заданных кодов в PDF-документе. Находит требуемые коды, вырезает соответствующие страницы и сохраняет их в новый PDF-файл.

- **`fix_lines.py`**  
  Скрипт для замены двойных линий на одинарные в выгруженных файлах, что упрощает их нарезку после печати.

## Сборка исполняемых файлов

Для преобразования Python-скриптов в исполняемые файлы, используйте `PyInstaller`. Следуйте инструкциям в указанных статьях и примерах.

### Установка PyInstaller

```shell
python -m pip install pyinstaller
```

### Создание исполняемых файлов

#### Для Windows

```shell
python -m PyInstaller --hidden-import os --hidden-import PyPDF2 --onefile --add-data "watermark.pdf;." .\fix_lines.py
```

или

```shell
python -m PyInstaller --onefile --add-data "watermark.pdf;." .\fix_lines.py
```

#### Для macOS

```shell
python3 -m PyInstaller --add-data "watermark.pdf:files" fix_lines.py
```

### Полезные ссылки

- [Как сделать из Python-скрипта исполняемый файл](https://habr.com/ru/companies/slurm/articles/746622/)
- [PyInstaller Documentation](https://pythonru.com/biblioteki/pyinstaller)
- [StackOverflow: No module named 'PyPDF2' error](https://stackoverflow.com/questions/39241643/no-module-named-pypdf2-error)
- [StackOverflow: How to include files with PyInstaller](https://stackoverflow.com/questions/53587322/how-do-i-include-files-with-pyinstaller)

---
