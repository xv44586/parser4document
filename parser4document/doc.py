# -*- coding: utf-8 -*-
# @Date    : 2020/9/25
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : doc.py.py
"""
转为.docx 后调用docx parser 统一处理
"""
import platform
import os

from .docx import DocXParser

is_windows = False
if platform.system() == 'Windows':
    is_windows = True

if is_windows:
    import win32com.client


class DocParser(DocXParser):
    def __init__(self, word_path, is_windows=is_windows):
        self.doc_path = word_path
        self.is_windows = is_windows
        word_path = self.doc2docx(word_path)
        super(DocParser, self).__init__(word_path)

    def doc2docx(self, path):
        if is_windows:
            return self.doc2docx_windows(path)
        return self.doc2docx_linux(path)

    @staticmethod
    def doc2docx_windows(path, remove=False):
        w = win32com.client.Dispatch('Word.Application')
        w.Visible = 0
        w.DisplayAlerts = 0
        doc = w.Documents.Open(path)
        newpath = os.path.splitext(path)[0] + '.docx'
        doc.SaveAs(newpath, 12, False, "", True, "", False, False, False, False)
        doc.Close()
        w.Quit()
        if remove:
            os.remove(path)
        return newpath

    @staticmethod
    def doc2docx_linux(path, remove=False):
        new_path = path.replace('.doc', '.docx')
        cmd = 'antiword {} > {}'.format(path, new_path)
        os.system(cmd)
        if remove:
            cmd = 'rm -v {}'.format(path)
            os.system(cmd)
        return new_path
