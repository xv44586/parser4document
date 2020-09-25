# -*- coding: utf-8 -*-
# @Date    : 2020/9/25
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : parse_doc.py.py

import os

from parser4document.doc import DocParser

cur_path = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.dirname(cur_path))
doc_name = '彭于晏.doc'
doc_path = os.path.join(parent_dir, 'docs', doc_name)
parser = DocParser(doc_path)
doc = parser.read()
print('doc: ', doc)

textbox = parser.extract_textbox()
print('textbox: ', textbox)

with open(doc_path.replace('.docx', '.txt'), 'w', encoding='utf8') as f:
    for content in doc:
        t = content['type']
        v = content['content']
        if t == 'text':
            print(v)
            f.write(''.join(v) + '\n')
        elif t == 'table':
            f.write('\n'.join(['\t'.join([c['text'] for c in row]) for row in v]) + '\n')