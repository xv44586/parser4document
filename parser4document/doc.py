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
from .utils import format


is_windows = False
if platform.system() == 'Windows':
    is_windows = True

if is_windows:
    import win32com.client

else:
    import subprocess
    import errno


class DocParser(DocXParser):
    def __init__(self, word_path, is_windows=is_windows):
        self.doc_path = word_path
        self.is_windows = is_windows
        self.word_path = None

    def read(self, with_textbox=False, verbose=False):
        if self.is_windows:
            new_path = self.doc2docx_windows(self.doc_path)
            self.word_path = new_path
            return super(DocParser, self).read(with_textbox, verbose)
        else:
            # use antiword to parse doc
            text = self.doc2docx_linux(self.doc_path)
            self.word_path = self.doc_path
            text = format(text.decode())
            if verbose:
                print('text: ', text)

            return [{'type': 'text', 'content': text, 'runs': []}]

    def run(self, args):
        """Run ``command`` and return the subsequent ``stdout`` and ``stderr``
        as a tuple. If the command is not successful, this raises a
        :exc:`textract.exceptions.ShellError`.
        """

        # run a subprocess and put the stdout and stderr on the pipe object
        try:
            pipe = subprocess.Popen(
                args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                # File not found.
                # This is equivalent to getting exitcode 127 from sh
                raise Exception(
                    ' '.join(args), 127, '', '',
                )

        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise Exception(
                ' '.join(args), pipe.returncode, stdout, stderr,
            )

        return stdout, stderr

    def doc2docx_windows(self, path, remove=False):
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

    def doc2docx_linux(self, path, remove=False):
        stdout, _ = self.run(['antiword', path])
        return stdout
