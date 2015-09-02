# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'
__copyright__ = "gentrify  Copyright (C) 2015  Steven Cutting"
__license__ = "AGPL"
from . import(__title__, __version__, __credits__, __maintainer__, __email__,
              __status__)
__title__
__version__
__credits__
__maintainer__
__email__
__status__


# import bs4
from bs4 import BeautifulSoup

import logging
LOG = logging.getLogger(__name__)


def is_html(html, test=True):
    if test and '<html' not in html:
        return html
    return BeautifulSoup(html, 'lxml').text
