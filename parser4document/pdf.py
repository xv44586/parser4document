# -*- coding: utf-8 -*-
# @Date    : 2020/9/23
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : pdf.py
"""
使用pdfplumber 按页（page）读取pdf内容：对text 内容区分table 内与 table 外，对图片格式，直接返回其bytes

[pdfplumber](https://github.com/jsvine/pdfplumber)
"""

import pdfplumber
from PIL import Image
from io import BytesIO
import base64
import os
import re
from collections import defaultdict

from .utils import format


class PDFParser(object):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf = pdfplumber.open(pdf_path)
        self.tabel_settings = {
            "vertical_strategy": 'lines',
            "horizontal_strategy": 'lines',
            "snap_tolerance": 10,
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
            text.append([format(cell).replace('\n', '') for cell in row if cell])

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
            text = page.filter(not_within_bboxes).extract_text()
            return format(text)
        else:
            return format(page.extract_text())

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
                img = self.read_img(page, save2disk=True, verbose=verbose)

            content.append({
                'text': text,
                'table': table_content,
                'img': img
            })

        return content

    def _get_image_name(self, name, verbose=False):
        """如果已存在同名文件，则增加后缀直到为合法文件名"""
        path = os.path.dirname(self.pdf_path)
        safe_name = os.path.join(path, name)
        if not os.path.exists(safe_name):
            return safe_name
        else:
            idx = 0
            name_parts = name.split('.')
            if len(name_parts) == 1:
                name_parts.append('.png')
                if verbose:
                    print('warning: image name "{}" not has suffix!'.format(name))
            flag = True
            name_pre, name_suffix = name_parts
            while flag:
                new_name = name_pre + '-%d' % idx + name_suffix
                if os.path.exists(os.path.join(path, new_name)):
                    idx += 1
                else:
                    flag = False

            return os.path.join(path, new_name)

    def read_img(self, page, save2disk=False, verbose=False):
        """抽取当前page内的图片，并转为base64编码后的结果
        """
        img_str = []
        for img in page.images:
            name = img['name']
            img_stream = img['stream']
            img_bytes = img_stream.get_data()
            b64_str = base64.b64encode(img_bytes)
            img_str.append(b64_str)
            if save2disk:
                img = Image.open(BytesIO(img_bytes))
                img_name = self._get_image_name(name, verbose)
                img.save(img_name, format='png')
            if verbose:
                show_bytes(img_bytes)

        return img_str

    def cut_page_text(self, page):
        """利用title 关键字切分内容，其中  'o' 是未知type"""
        title = {'education': ['教育背景', '教育经历'],
                 'awards': ['获奖情况', ],
                 'self-assessment': ['个人评价', ],
                 'info': ['个人信息', '个人总结'],
                 'work_exp': ['项目经历', '项目经验'],
                 'company_exp': ['工作经验'],
                 'skills': ['职业技能', '专业技能']}

        def has_title(text):
            pat = '|'.join(['|'.join(v) for v in title.values()])
            return list(re.finditer(pat, text))

        def is_title(text):
            ts = []
            for v in title.keys():
                ts.expand(v)
            return text.strip().replace(' ', '') in ts

        def drop_none_text(text):
            """非字符，如空格，\n, \t等"""
            return re.sub(r"[ \t\n]+", "", text)

        def get_normalize_title(title_text):
            """返回标准title"""
            titles = {}
            for _, v in title.items():
                for t in v:
                    titles[t] = v[0]

            return titles[title_text]

        text = page.extract_text()
        #     text = re.split('\n[ ]{0,10}\n', text)
        if type(text) != list:
            text = [text]
        coll = defaultdict(list)
        for seg in text:
            t_span = has_title(text)
            if not t_span:
                coll['o'].append(seg)
            else:
                last_title_start, last_title_end = 0, 0
                # 得到多个titlespan
                for ts in t_span:

                    title_start, title_end = ts.span()
                    if last_title_start < last_title_end:
                        t = get_normalize_title(seg[last_title_start: last_title_end])
                        coll[t].append(seg[last_title_end: title_start])
                    else:
                        coll['o'].append(seg[last_title_end: title_start])

                    last_title_start, last_title_end = title_start, title_end

                # 收尾
                if last_title_start < last_title_end:
                    t = get_normalize_title(seg[last_title_start: last_title_end])
                    coll[t].append(seg[last_title_end:])
                else:
                    coll['o'].append(seg[last_title_end:])

        return coll


def show_bytes(bytes_blob):
    stream = BytesIO(bytes_blob)
    Image.open(stream)

