# -*- coding: utf-8 -*-

import os
import sys
import codecs
import subprocess

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class TestRunner(TestCommand):
    user_options = []

    def run(self):
        raise SystemExit(subprocess.call([sys.executable, 'runtests.py']))
    

def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name="django-cached-modelforms",
    version="0.2.2",
    license='BSD License',

    install_requires=[
        'six',
    ],
    requires=[
        'Django (>=1.4)',
    ],

    description="ModelChoiceField implementation that can accept lists of objects, not just querysets",
    long_description=read('README.rst'),

    author='Vlad Starostin',
    author_email='drtyrsa@yandex.ru',

    url='https://github.com/drtyrsa/django-cached-modelforms',
    download_url='https://github.com/drtyrsa/django-cached-modelforms/zipball/master',

    packages=find_packages(exclude=('example*', '*.tests*')),
    include_package_data=True,

    tests_require=[
    ],
    cmdclass={
        'test': TestRunner,
    },

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
