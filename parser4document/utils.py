# -*- coding: utf-8 -*-
# @Date    : 2020/9/25
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : utils.py


def Q2B(uchar):
    """单个字符 全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:  # 空格
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def stringQ2B(ustring):
    """字符串全角转半角"""
    return ''.join(Q2B(uchar) for uchar in ustring)


def format(text):
    """格式化文本"""
    if type(text) != list:
        text = [text]

    format_text = []
    for t in text:
        b_text = stringQ2B(t)
        format_text.append(b_text)

    if len(format_text) < 2:
        return format_text[0]
    return format_text
