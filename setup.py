# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-cached-modelforms",
    version = "0.1.0",
    license = "BSD",
    description = "ModelChoiceField implementation that can accept lists of objects, not just querysets",
    long_description = read('README.rst'),
    author = "Vlad Starostin",
    author_email = "drtyrsa@yandex.ru",
    packages = find_packages('cached_modelforms'),
    package_dir = {'': 'cached_modelforms'},
    install_requires= ['setuptools'],
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