# -*- coding: utf-8 -*-
# @Date    : 2020/9/23
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : parse_pdf.py
import json
import os

from parser4document.pdf import PDFParser


cur_path = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.dirname(cur_path))
pdf_name = '彭于晏.pdf'
pdf_path = os.path.join(parent_dir, 'docs', pdf_name)
pdf_parser = PDFParser(pdf_path)
content = pdf_parser.read(verbose=True)

txt_path = pdf_path.replace('.pdf', '.txt')

with open(txt_path, 'w', encoding='utf8') as f:
    for c in content:
        if c['text']:
            f.write(c['text'] + '\n')
        if c['table']:
            f.write('\n'.join([' '.join([c.replace('\n', '') for c in row if c]) for row in c['table'] if row]))

