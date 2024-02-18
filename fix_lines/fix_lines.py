'''
Скрипт для замены двойных линий на одинарные в выгруженных файлах для удобства нарезки после печати.
'''
# https://www.pythonsos.com/libraries/drawing-lines-on-pdf-with-python/?expand_article=1
import os
import PyPDF2

import PdfReader

def draw_lines_on_pdf(input_pdf_path, output_pdf_path, line_coordinates):
    with open(input_pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfFileReader(file)
        page = pdf.getPage(0)
        page_width = page.mediaBox.getWidth()
        page_height = page.mediaBox.getHeight()

        # content_stream = page['/Contents'].getObject()
        # content_stream.append(PyPDF2.pdf.ContentStream('qn'))
        #
        # for coordinates in line_coordinates:
        #     x1, y1, x2, y2 = coordinates
        #     content_stream.append(PyPDF2.pdf.ContentStream(f'{x1} {y1} {x2} {y2} re Sn'))
        #
        # content_stream.append(PyPDF2.pdf.ContentStream('Qn'))
        # page['/Contents'] = content_stream
        #
        # with open(output_pdf_path, 'wb') as output_file:
        #     pdf.write(output_file)


if __name__ == "__main__":
    # Example usage
    print(os.listdir())
    line_coordinates = [(100, 100, 200, 200), (300, 300, 400, 400)]
    draw_lines_on_pdf('input.pdf', 'output.pdf', line_coordinates)


