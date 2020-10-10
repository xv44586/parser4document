# -*- coding: utf-8 -*-
# @Date    : 2020/10/10
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : split_text.py
import os
import re

from parser4document.docx import DocXParser
from parser4document.utils import split_text_by_keywords

cur_path = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.dirname(cur_path))
docx_name = '彭于晏.docx'
doc_path = os.path.join(parent_dir, 'docs', docx_name)
parser = DocXParser(doc_path)
doc = parser.read(with_textbox=True)


def get_plan_text(word_content):
    lines = []

    for content in word_content:
        if content['type'] == 'table':
            text = '\n'.join(['\t'.join([c['text'] for c in l]) for l in content['content']])
            lines.append(text)
        elif content['type'] == 'text':
            lines.append(content['content'])
        elif content['type'] == 'textbox' and content['content']:
            lines.extend(content['content'])
    return lines


def cleanup(text):
    text = re.sub(r'[\n]{2,}', '\n', text)
    text = re.sub(r'[\t]{2,}', '\t', text)
    text = re.sub('[ ]+', '', text)
    return text.strip()


plan_text = get_plan_text(doc)
segs = split_text_by_keywords('\n'.join([cleanup(line) for line in plan_text]))

for k, c in segs.items():
    c = [k] + [cleanup(t) for t in c]
    print('\n'.join(c))
    print('\n' + '-' * 30 + '\n')
