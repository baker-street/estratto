# -*- coding: utf-8 -*-
"""
gentrify  Copyright (C) 2015  Steven Cutting - License: gentrify/LICENSE
"""
from setuptools import setup, find_packages

with open("README.md") as fp:
    THE_LONG_DESCRIPTION = fp.read()


setup(
    name='gentrify',
    version='0.1.0',
    license='GNU GPL v3+',
    description="Makes misc files usable for nlp.",
    long_description=THE_LONG_DESCRIPTION,
    classifiers=['Topic :: NLP',
                 'Topic :: Text cleaning',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Data Scientists',
                 'Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 2.7',
                 'License :: GNU GPL v3+',
                 ],
    keywords='nlp encoding text plaintext preprocessing',
    author='Steven Cutting',
    author_email='steven.e.cutting@linux.com',
    packages=find_packages(exclude=('scripts', 'tests')),
    # zip_safe=False,
    install_requires=['chardet',
                      'ftfy>=4,<5',
                      'arrow',
                      'smart_open',  # TODO (steven_c) phase out smart_open
                      'beautifulsoup4',
                      'pathlib',
                      'docx',
                      'pdfminer',
                      'lxml',
                      ],
    )
