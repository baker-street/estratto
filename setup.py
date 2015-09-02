# -*- coding: utf-8 -*-
"""
estratto  Copyright (C) 2015  Steven Cutting - License AGPL: estratto/LICENSE
"""

from estratto import(__title__, __version__, __status__)


from setuptools import setup, find_packages

with open("README.md") as fp:
    THE_LONG_DESCRIPTION = fp.read()

TESTDEPEND = ['pytest']
# DEVDEPEND = []
# Work on making python-magic optional.
FULLDEPEND = ['click', 'cchardet', 'python-magic', 'python-docx', 'xlrd']

setup(name=__title__,
      version=__version__,
      license='GNU AGPL',
      description="Makes misc files usable for nlp.",
      long_description=THE_LONG_DESCRIPTION,
      classifiers=['Topic :: NLP :: Text cleaning',
                   'Topic :: NLP :: Initial processing',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Data Scientists',
                   'Development Status ::' + __status__,
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'License :: GNU AGPL',
                   'Copyright :: estratto  Copyright (C) 2015  Steven Cutting',
                   'Status ::' + __status__,
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
                        'unidecode',
                        ],
      extras_require={
          # 'dev': DEVDEPEND,
          'full': FULLDEPEND,
          'test': TESTDEPEND,
      }
      )
