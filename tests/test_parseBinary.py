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


import os
from gentrify.parseBinary import parse_binary

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)

TESTDATADIR = 'testdata/The_Adventures_of_Sherlock_Holmes/from_libre_office/'


def test__parse_binary__parse_doc():
    fname = TESTDATADIR + 'pg1661.doc'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) > 20)
    assert(prsd['filename'] == fname)


def test__parse_binary__parse_docx():
    fname = TESTDATADIR + 'pg1661.docx'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) > 20)
    assert(prsd['filename'] == fname)


def test__parse_binary__parse_pdf():
    fname = TESTDATADIR + 'pg1661_PDF.pdf'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) >= 20)
    assert(prsd['filename'] == fname)


def test__parse_binary__parse_pdf_FDF():
    fname = TESTDATADIR + 'pg1661_FDF.pdf'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) >= 20)
    assert(prsd['filename'] == fname)


def test__parse_binary__parse_pdf_HTML():
    fname = TESTDATADIR + 'pg1661_HTML.pdf'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) >= 20)
    assert(prsd['filename'] == fname)


def test__parse_binary__parse_pdf_XML():
    fname = TESTDATADIR + 'pg1661_XML.pdf'
    prsd = parse_binary(fname=fname)
    assert(len(prsd['body']) >= 20)
    assert(prsd['filename'] == fname)


if __name__ == '__main__':
    test__parse_binary__parse_doc()
    test__parse_binary__parse_docx()
    test__parse_binary__parse_pdf()
    test__parse_binary__parse_pdf_FDF()
    test__parse_binary__parse_pdf_HTML()
    test__parse_binary__parse_pdf_XML()
