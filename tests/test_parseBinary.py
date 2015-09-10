# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'
__copyright__ = "estratto  Copyright (C) 2015  Steven Cutting"
__license__ = "AGPL"
from estratto import(__title__, __version__, __credits__, __maintainer__,
                     __email__, __status__)
__title__
__version__
__credits__
__maintainer__
__email__
__status__


import os
from os.path import join

# import pytest

from estratto.parseBinary import parse_binary
from estratto.utils import spelunker_gen

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)

TESTDIR = "testdata/The_Adventures_of_Sherlock_Holmes/from_libre_office/mini/"
TESTDIRLONG = 'testdata/The_Adventures_of_Sherlock_Holmes/from_libre_office/'


def test__parse_binary__parse_doc__test_if_run_and_len_20():
    fname = join(TESTDIR, 'doc/pure_doc/pg1661-mini.doc')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) > 20)


def test__parse_binary__parse_docx__test_if_run_and_len_20():
    fname = join(TESTDIR, 'doc/pure_doc/pg1661-mini.docx')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) > 20)


def test__parse_binary__parse_pdf__test_if_run_and_len_20():
    fname = join(TESTDIR, 'pdf/pg1661-mini_PDF.pdf')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) >= 20)


def test__parse_binary__parse_pdf_FDF__test_if_run_and_len_20():
    fname = join(TESTDIR, 'pdf/pg1661-mini_FDF.pdf')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) >= 20)


def test__parse_binary__parse_pdf_HTML__test_if_run_and_len_20():
    fname = join(TESTDIR, 'pdf/pg1661-mini_HTML.pdf')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) >= 20)


def test__parse_binary__parse_pdf_XML__test_if_run_and_len_20():
    fname = join(TESTDIR, 'pdf/pg1661-mini_XML.pdf')
    prsd = parse_binary(fname=fname)
    assert(len(prsd) >= 20)


def compr_binary_parse_on_files(fnamelist):
    assert(len(fnamelist) >= 2)
    for i, fname in enumerate(fnamelist):
        new = parse_binary(fname=fname).replace(' ', '').replace('\n', '')
        assert(len(new) > 20)
        if i == 0:
            old = new
        else:
            assert(old == new)
            old = new


def test__parse_binary__compare_pdfs__XML_PDF_FDF_HTML():
    fnamelist = list(spelunker_gen(join(TESTDIR, 'pdf/')))
    compr_binary_parse_on_files(fnamelist)


def test__parse_binary__compare_docs__doc_docx_OpenOfficXML():
    fnamelist = list(spelunker_gen(join(TESTDIR, 'doc/pure_doc')))
    compr_binary_parse_on_files(fnamelist)


def test__parse_binary__compare_docs__doc_docx():
    fnamelist = list(spelunker_gen(join(TESTDIR, 'doc/pure_doc')))
    compr_binary_parse_on_files(fnamelist)


if __name__ == '__main__':
    test__parse_binary__parse_doc__test_if_run_and_len_20()
    test__parse_binary__parse_docx__test_if_run_and_len_20()
    test__parse_binary__parse_pdf__test_if_run_and_len_20()
    test__parse_binary__parse_pdf_FDF__test_if_run_and_len_20()
    test__parse_binary__parse_pdf_HTML__test_if_run_and_len_20()
    test__parse_binary__parse_pdf_XML__test_if_run_and_len_20()
    test__parse_binary__compare_pdfs__XML_PDF_FDF_HTML()
