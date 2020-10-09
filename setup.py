# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import find_packages, setup


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding="utf-8").read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-cached-modelforms",
    version=find_version("cached_modelforms", "__init__.py"),
    license="BSD License",
    install_requires=[
        "six",
    ],
    requires=[
        "Django (>=1.4)",
    ],
    description="ModelChoiceField implementation that can accept lists of objects, not just querysets",
    long_description=read("README.rst"),
    author="Vlad Starostin",
    author_email="drtyrsa@yandex.ru",
    maintainer="Basil Shubin",
    maintainer_email="basil.shubin@gmail.com",
    url="https://github.com/drtyrsa/django-cached-modelforms",
    download_url="https://github.com/drtyrsa/django-cached-modelforms/zipball/master",
    packages=find_packages(exclude=("example*", "*.tests*")),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
