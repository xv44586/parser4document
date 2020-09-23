# -*- coding: utf-8 -*-
# @Date    : 2020/9/21
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : parse_docx.py
from parser4document.docx import DocXParser

doc_path = '../docs/彭于晏.docx'
parser = DocXParser(doc_path)
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