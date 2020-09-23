文件解析器，解析包括.doc/.docx/pdf文件

# doc文件

## Windows 平台
直接处理 .doc 对表格处理不友好，如有合并单元格时会报错而无法读取，所以利用win32com来将其转换为.docx来处理。
```python
import os


def doc2docx(path):
    w = win32com.client.Dispatch('Word.Application')
    w.Visible = 0
    w.DisplayAlerts = 0
    doc = w.Documents.Open(path)
    newpath = os.path.splitext(path)[0] + '.docx'
    doc.SaveAs(newpath, 12, False, "", True, "", False, False, False, False)
    doc.Close()
    w.Quit()
    os.remove(path)
    return newpath
```
## Linux
通用的方案是利用<a href='https://textract.readthedocs.io/en/latest/installation.html'>textract</a>来提取内容，其backend是
<a href='http://www.winfield.demon.nl/'>antiword</a>，利用antiword 也可以转为.docx，所以也是选择将.doc转为.docx来处理。
```shell
antiword path-to-doc > path-to-docx
```
# docx文件
.docx文件的解析使用<a href='https://python-docx.readthedocs.io/en/latest/'>python-docx</a>,他可以帮助我们提取段落、表格、附件等内容。

# pdf文件
pdf文件解析使用<a href='https://github.com/jsvine/pdfplumber'>pdfplumber</a>,他底层使用<a href='https://github.com/pdfminer/pdfminer.six'>pdfminer.six</a>,
在此之上，增加了对表格内容的组织，所以除了读取内容外，针对表格还可以返回其结构化结果。
