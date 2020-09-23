# -*- coding: utf-8 -*-
# @Date    : 2020/9/23
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : pdf.py
"""

"""

import pdfplumber
from PIL import Image
from io import BytesIO


class PDFParser(object):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf = pdfplumber.open(pdf_path)
        self.tabel_settings = {
            "vertical_strategy": 'lines',
            "horizontal_strategy": 'lines'
            # "explicit_vertical_lines": self.curves_to_edges(p.curves + p.edges),
            # "explicit_horizontal_lines": self.curves_to_edges(p.curves + p.edges),
            # "intersection_y_tolerance": 10,
        }

    def curves_to_edges(self, cs):
        """See https://github.com/jsvine/pdfplumber/issues/127"""
        edges = []
        for c in cs:
            edges += pdfplumber.utils.rect_to_edges(c)
        return edges

    def read_table_from_page(self, page):
        text = []
        if type(page) == int:
            page = self.pdf.pages[page]

        table = page.extract_table(table_settings=self.tabel_settings)
        for row in table:
            text.append([cell.replace('\n', '') for cell in row if cell])

        return text

    def read_text_from_page(self, page, without_table=True):
        """
        读取当前page中内容，可选所有内容和table 外内容
        :param page:
        :param without_table:
        :return:
        """
        if type(page) == int:
            page = self.pdf.pages[page]

        # Get the bounding boxes of the tables on the page.
        bboxes = [table.bbox for table in page.find_tables(table_settings=self.tabel_settings)]

        def not_within_bboxes(obj):
            """Check if the object is in any of the table's bbox."""

            def obj_in_bbox(_bbox):
                """See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404"""
                v_mid = (obj["top"] + obj["bottom"]) / 2
                h_mid = (obj["x0"] + obj["x1"]) / 2
                x0, top, x1, bottom = _bbox
                return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)

            return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

        if without_table:
            return page.filter(not_within_bboxes).extract_text()
        else:
            return page.extract_text()


    def read_img(self, page, show=False):
        if type(page) == int:
            page = self.pdf.pages[page]

        images = page.images
        img_bytes = []
        if len(images) > 0:
            for image in images:
                img_stream = image['stream']
                bytes = img_stream.get_data()
                img_bytes.append(bytes)

        if show:
            for ib in img_bytes:
                show_bytes(ib)

        return img_bytes

    def read(self, with_img=True, verbose=True):
        content = []
        img = None
        text = None
        table_content = None

        for _, page in enumerate(self.pdf.pages):
            text = self.read_text_from_page(page, without_table=True)
            table_content = self.read_table_from_page(page)

            if verbose:
                print('page at {}:'.format(_))
                print('text :')
                print(text)
                print('table: ')
                print('\n'.join([' '.join(row) for row in table_content]))
            if with_img:
                img = self.read_img(page, verbose)

            content.append({
                'text': text,
                'table': table_content,
                'img': img
            })

        return content


def show_bytes(bytes_blob):
    stream = BytesIO(bytes_blob)
    Image.open(stream)

