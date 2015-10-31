# -*- coding:utf-8 -*-

import os
import codecs

from setuptools import setup, find_packages

from cached_modelforms import __version__


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name="django-cached-modelforms",
    version=__version__,
    license='BSD License',

    install_requires=[
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

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
