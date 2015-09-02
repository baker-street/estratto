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
from json import dump
from estratto import(parseEmail, utils)
from estratto.parseEmail import email_whole_parse_from_str

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)


def test__email_whole_parse_from_str__only_run__1():
    txt1 = utils.load_file('sample_enron_email.')
    prsd = email_whole_parse_from_str(txt1)
    with open('sample_enron_email_1.json', 'w+') as fp:
        dump(prsd, fp, indent=4)


def test__email_whole_parse_from_str__only_run__2():
    txt1 = utils.load_file('sample_enron_email.eml')
    prsd = email_whole_parse_from_str(txt1)
    with open('sample_enron_email_2.json', 'w+') as fp:
        dump(prsd, fp, indent=4)


# ----------------------------------------------------------------------------
# Testing for emails
def test__is_an_email_from_cont():
    txt1 = utils.load_file('sample_enron_email.')
    txt2 = utils.load_file('sample_enron_email.eml')
    assert(parseEmail.is_an_email_from_cont(text=txt1))
    assert(parseEmail.is_an_email_from_cont(text=txt2))


if __name__ == '__main__':
    test__email_whole_parse_from_str__only_run__1()
    test__email_whole_parse_from_str__only_run__2()
    test__is_an_email_from_cont()
