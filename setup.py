#!/usr/bin/env python
# -*- coding: utf8 -*-
# @Date    : 2020/6/29
# @Author   : mingming.xu
# @Email    : xv44586@gmail.com

from setuptools import setup, find_packages

setup(
    name='parser4document',
    version='0.0.3',
    description='an toolkit for parse doc/docx/pdf document',
    long_description='toolkit4nlp: https://github.com/xv44586/parser4document',
    license='Apache License 2.0',
    url='https://github.com/xv44586/parser4document',
    author='xv44586',
    author_email='xv44586@gmail.com',
    install_requires=['python-docx'],
    packages=find_packages()
)
