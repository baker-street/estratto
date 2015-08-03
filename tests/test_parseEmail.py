# -* coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'

import os

from gentrify import(parseEmail, utils)

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)

# ----------------------------------------------------------------------------
# Testing for emails
def test__is_an_email_from_cont():
    txt1 = utils.load_file('sample_enron_email.')
    txt2 = utils.load_file('sample_enron_email.eml')
    assert(parseEmail.is_an_email_from_cont(txt=txt1))
    assert(parseEmail.is_an_email_from_cont(txt=txt2))
