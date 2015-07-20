# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/14/2015'

import os

from gentrify import utils
from gentrify.fixEncoding import(sane_unicode,
                                 __insane_unicode,
                                 make_unicode_dang_it,
                                 auto_eng_unicode_dang_it,
                                 convert_datastruct_text)

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)


# basic tests
TEST_STRING_1 = 'If numbers arenâ€™t beautiful, \
I donâ€™t know what is. â€“Paul ErdÅ‘s'
TEST_STRING_2 = '“mÃ¡s”'
TEST_STRING_3 = '“mÃƒÂ¡s”'
TEST_STRING_4 = '“€”'


def test_sane_unicode1():
    res = sane_unicode(TEST_STRING_1)
    assert(res ==
           u"If numbers aren't beautiful, I don't know what is. –Paul Erdős")
    assert(isinstance(res, unicode))


def test_insane_unicode1():
    res = __insane_unicode(TEST_STRING_1)
    assert(res ==
           u"If numbers aren't beautiful, I don't know what is. –Paul Erdős")
    assert(isinstance(res, unicode))


def test_make_unicode_dang_it1():
    res = make_unicode_dang_it(TEST_STRING_1)
    assert(res ==
           u"If numbers aren't beautiful, I don't know what is. –Paul Erdős")
    assert(isinstance(res, unicode))


def test_auto_unicode_dang_it1():
    res = auto_eng_unicode_dang_it(TEST_STRING_1)
    assert(res ==
           u"If numbers aren't beautiful, I don't know what is. -Paul Erdos")
    assert(isinstance(res, unicode))


def test_sane_unicode2():
    res = sane_unicode(TEST_STRING_2)
    assert(res ==
           u'"más"')
    assert(isinstance(res, unicode))


def test_auto_unicode_dang_it2():
    res = auto_eng_unicode_dang_it(TEST_STRING_2)
    assert(res ==
           u'"mas"')
    assert(isinstance(res, unicode))


def test_sane_unicode3():
    res = sane_unicode(TEST_STRING_3)
    assert(res ==
           u'"más"')
    assert(isinstance(res, unicode))


def test_auto_unicode_dang_it3():
    res = auto_eng_unicode_dang_it(TEST_STRING_3)
    assert(res ==
           u'"mas"')
    assert(isinstance(res, unicode))


def test_sane_unicode4():
    res = sane_unicode(TEST_STRING_4)
    assert(res ==
           u'"€"')
    assert(isinstance(res, unicode))


def test_auto_unicode_dang_it4():
    res = auto_eng_unicode_dang_it(TEST_STRING_4)
    assert(res ==
           u'"EUR"')
    assert(isinstance(res, unicode))


def test__convert_datastruct_text():
    smpldatastruct = utils.load_json('sample_parsed_email.json')
    tounicode = convert_datastruct_text(smpldatastruct,
                                        convertfunc=unicode)
    tostr = convert_datastruct_text(smpldatastruct,
                                    convertfunc=str)
    nochange = convert_datastruct_text(smpldatastruct,
                                       convertfunc=lambda a: a)
    assert(smpldatastruct == tounicode)
    assert(smpldatastruct == tostr)
    assert(smpldatastruct == nochange)
