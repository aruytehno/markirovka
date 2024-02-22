# markirovka
Проект содержащий скрипты для работы с системой "Честный знак"

```text
api_crpt.py
Скрипт предназначен для проверки валидности кодов - находятся ли они в обороте или нет и прочих статусов.
```

```text
find_txt_pdf.py
Скрипт предназначен для поиска требуемых кодов в pdf документе с общим массивом кодов после выгрузки, сохраняя вырезанные в новый pdf файл.
```

```text
fix_lines.py
Скрипт предназначен для замены двойных линий на одинарные в выгруженных файлах для удобства нарезки после печати.
```

[part 1 Как сделать из Python-скрипта исполняемый файл](https://habr.com/ru/companies/slurm/articles/746622/)
[part 2 pyinstaller](https://pythonru.com/biblioteki/pyinstaller)
[part 3 stackoverflow](https://stackoverflow.com/questions/39241643/no-module-named-pypdf2-error)
```shell
python -m pip install pyinstaller
python -m PyInstaller --hidden-import os --hidden-import PyPDF2 --onefile --add-data "watermark.pdf;." .\fix_lines.py
python -m PyInstaller --onefile --add-data "watermark.pdf;." .\fix_lines.py
```