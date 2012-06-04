#!/usr/bin/env python
# -*- coding:utf-8 -*-
from distutils.core import setup


setup(
    name = "django-cached-modelforms",
    version = '0.2.1',
    license = 'BSD',
    description = "ModelChoiceField implementation that can accept lists of objects, not just querysets",
    long_description = open('README.rst').read(),
    author = 'Vlad Starostin',
    author_email = 'drtyrsa@yandex.ru',
    packages = ['cached_modelforms',
                'cached_modelforms.tests',
                'cached_modelforms.tests.utils'],
    classifiers = [
        'Development Status :: 1 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
