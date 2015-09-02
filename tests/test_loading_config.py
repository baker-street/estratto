# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'
__copyright__ = "gentrify  Copyright (C) 2015  Steven Cutting"
__license__ = "AGPL"
from gentrify import(__title__, __version__, __credits__, __maintainer__,
                     __email__, __status__)
__title__
__version__
__credits__
__maintainer__
__email__
__status__


from gentrify import(parseEmail, parseBinary)


def test_email_exts():
    assert(isinstance(parseEmail.EMAILEXTS, set))


def test_email_address_headers():
    assert(isinstance(parseEmail.EXTRA_ADDRESS_HEADERS, list))


def test_email_extra_headers():
    assert(isinstance(parseEmail.EXTRA_HEADERS, list))


def test_ok_file_exts():
    assert(isinstance(parseBinary.OKEXT, set))


if __name__ == '__main__':
    test_email_exts()
    test_email_address_headers()
    test_email_extra_headers()
    test_ok_file_exts()
