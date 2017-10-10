#!/usr/bin/env python
# encoding_ utf8

from setuptools import setup, find_packages
import codecs
import os
import re

def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='rest_framework_filterdsl',
    version=find_version('rest_framework_filterdsl', "__init__.py"),
    description='This package provides a small domain-specific language for filtering and sorting '
            + 'the views provided using Django REST framework by GET parameters.',
    description_long=read('README.md'),
    author='Nico Mandery',
    author_email='nico.mandery@dlr.de',
    install_requires=[
        'djangorestframework>=3.6',
        'python-dateutil>=2.6.1',
        'pyparsing>=2.2.0',
        'Django>=1.11',
    ],
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    platforms=['Platform Indipendent'],
    keywords=['django', 'rest-framework', 'orm'],
)
