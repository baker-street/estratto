# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'


from gentrify import(parseEmail, parseBinary)


def test_email_exts():
    assert(isinstance(parseEmail.EMAILEXTS, set))


def test_email_address_headers():
    assert(isinstance(parseEmail.EXTRA_ADDRESS_HEADERS, list))


def test_email_extra_headers():
    assert(isinstance(parseEmail.EXTRA_HEADERS, list))


def test_ok_file_exts():
    assert(isinstance(parseBinary.OKEXT, set))
