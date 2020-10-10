# -*- coding: utf-8 -*-
# @Date    : 2020/9/25
# @Author  : mingming.xu
# @Email   : mingming.xu@zhaopin.com
# @File    : utils.py
from collections import defaultdict
import re


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


title_map = {'education': ['教育背景', '教育经历'],
             'awards': ['获奖情况', ],
             'self-assessment': ['个人评价', '关于我', 'About Me', '个人评估', '自我评价'],
             'info': ['个人信息', '个人总结', '个人简历', '简历', '个人简介', '基本信息'],
             'work_exp': ['项目经历', '项目经验', '实习经历', '实习经验'],
             'company_exp': ['工作经验', '工作经历'],
             'skills': ['职业技能', '专业技能', '个人技能', '能力认证'],
             'intention': ['求职意向', '职业目标', '求职目标']
             }


def has_title(text):
    pat = '|'.join(['|'.join(v) for v in title_map.values()])
    return list(re.finditer(pat, text))


def is_title(text):
    ts = []
    for v in title_map.keys():
        ts.expand(v)
    return text.strip().replace(' ', '') in ts


def drop_none_text(text):
    """非字符，如空格，\n, \t等"""
    return re.sub(r"[ \t\n]+", "", text)


def get_normalize_title(title_text):
    """返回标准title"""
    titles = {}
    for _, v in title_map.items():
        for t in v:
            titles[t] = v[0]

    return titles[title_text]


def split_text_by_keywords(text):
    """通过title关键字切分文本"""
    #     segs = re.split('\n[ ]{0,10}\n', text)
    segs = [text]
    coll = defaultdict(list)
    o = []  # no type
    for seg in segs:
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
