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


import sys
import os
import re

from gentrify import utils

if sys.version_info[0] >= 3:
    unicode = str  # adjusting to python3

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)


def test__get_file_suffixes__1():
    assert(utils.get_file_suffixes('/foo/bar/baz.txt') == '.txt')


def test__get_file_suffixes__2():
    assert(utils.get_file_suffixes('~/baz.txt') == '.txt')


def test__get_file_suffixes__3():
    assert(utils.get_file_suffixes('/foo/b.ar/baz.txt') == '.txt')


def test__get_file_suffixes__if_pathlib_is_installed():
    assert(utils.get_file_suffixes('/foo/bar/baz.tar.gz') == '.tar.gz')


def test___get_file_suffixes__opt_two__1():
    assert(utils._get_file_suffixes('/foo/bar/baz.tar.gz') == '.gz')


def test___get_file_suffixes__opt_two__2():
    assert(utils._get_file_suffixes('/foo/bar/baz.txt') == '.txt')


def test___get_file_suffixes__opt_two__3():
    assert(utils._get_file_suffixes('~/baz.txt') == '.txt')


def test__write_and_op_on_tmp():
    smpldata = 'data\ndata\n' * 3

    def readtmp(fname):
        with open(fname, mode='r') as fp:
            return fp.read()
    outpt = utils.write_and_op_on_tmp(smpldata, function=readtmp, suffix='.txt')
    assert(smpldata == outpt)


def test__write_and_op_on_tmp__and__sopen():
    smpldata = 'data\ndata\n' * 3

    def readtmp(fname):
        with utils.sopen(fname, mode='r') as fp:
            return fp.read()
    assert(smpldata ==
           utils.write_and_op_on_tmp(smpldata,
                                     function=readtmp,
                                     suffix='.txt'))


def test__load_json():
    test = utils.load_json(TEST_DIR + 'sample_parsed_email.json',
                           mode='r')
    assert(isinstance(test, list))


# ------------------------------------------------------------------------------
# Time Zone Normalization Functions.
TIME_STRING1 = 'Sat, 20 Jun 2015 09:15:18'
TIME_STRING2 = 'Sat, 20 Jun 2015 9:15:18'
TIME_STRINGS = [TIME_STRING1,
                TIME_STRING2,
                ]

NA_TIME_ZONE_ABRVS = {'EDT': '-0400',
                      'CST': '-0600',
                      'EST': '-0500',
                      'CDT': '-0500',
                      'MDT': '-0600',
                      'MST': '-0700',
                      'PDT': '-0700',
                      'PST': '-0800',
                      }

DIF_TZ_OFFSETS_FMT_1 = {'-04:00',
                        '-05:00',
                        '-06:00',
                        '-07:00',
                        '-08:00',
                        '+04:00',
                        '+05:00',
                        '+06:00',
                        '+07:00',
                        '+08:00',
                        '+00:00',
                        }

DIF_TZ_OFFSETS_FMT_2 = {'-0400',
                        '-0500',
                        '-0600',
                        '-0700',
                        '-0800',
                        '+0400',
                        '+0500',
                        '+0600',
                        '+0700',
                        '+0800',
                        '+0000',
                        }

NA_TIME_ZONE_CONVER_CACHED_RESs = {
    "Sat, 20 Jun 2015 09:15:18 EST": "2015-06-20T14:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 PDT": "2015-06-20T16:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 MST": "2015-06-20T16:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 CDT": "2015-06-20T14:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 MDT": "2015-06-20T15:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 EDT": "2015-06-20T13:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 CST": "2015-06-20T15:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 PST": "2015-06-20T17:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -0800": "2015-06-20T17:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -0400": "2015-06-20T13:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -0500": "2015-06-20T14:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -0600": "2015-06-20T15:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -0700": "2015-06-20T16:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -07:00": "2015-06-20T16:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -08:00": "2015-06-20T17:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -05:00": "2015-06-20T14:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -06:00": "2015-06-20T15:15:18+00:00",
    "Sat, 20 Jun 2015 09:15:18 -04:00": "2015-06-20T13:15:18+00:00",
    }


def test__TZ_PAT_1():
    for offset in DIF_TZ_OFFSETS_FMT_1:
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_1, tdstr1))
        assert(re.search(utils.TZ_PAT_1, tdstr2))


def test__TZ_PAT_1__unicode():
    for offset in DIF_TZ_OFFSETS_FMT_1:
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_1, unicode(tdstr1)))
        assert(re.search(utils.TZ_PAT_1, unicode(tdstr2)))


def test__TZ_PAT_2():
    for offset in DIF_TZ_OFFSETS_FMT_2:
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_2, tdstr1))
        assert(re.search(utils.TZ_PAT_2, tdstr2))


def test__TZ_PAT_2__unicode():
    for offset in DIF_TZ_OFFSETS_FMT_2:
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_2, unicode(tdstr1)))
        assert(re.search(utils.TZ_PAT_2, unicode(tdstr2)))


def test__TZ_PAT_3():
    for offset in NA_TIME_ZONE_ABRVS.keys():
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_3, tdstr1))
        assert(re.search(utils.TZ_PAT_3, tdstr2))


def test__TZ_PAT_3__unicode():
    for offset in NA_TIME_ZONE_ABRVS.keys():
        tdstr1 = TIME_STRING1 + ' ' + offset
        tdstr2 = TIME_STRING2 + ' ' + offset
        assert(re.search(utils.TZ_PAT_3, unicode(tdstr1)))
        assert(re.search(utils.TZ_PAT_3, unicode(tdstr2)))


def test__tz_abv_2_offset__test1():
    for abrv, offset in NA_TIME_ZONE_ABRVS.items():
        assert(utils.tz_abv_2_offset(abrv, abv2offsetdict=NA_TIME_ZONE_ABRVS) ==
               offset)


def test__tz_abv_2_offset__test1_unicode():
    for abrv, offset in NA_TIME_ZONE_ABRVS.items():
        assert(utils.tz_abv_2_offset(unicode(abrv),
                                     abv2offsetdict=NA_TIME_ZONE_ABRVS) ==
               unicode(offset))


def test__tz_abv_2_offset__test2():
    for abrv, offset in NA_TIME_ZONE_ABRVS.items():
        timestrabv = TIME_STRING1 + ' ' + abrv
        timestroffset = TIME_STRING1 + ' ' + offset
        assert(utils.tz_abv_2_offset(timestrabv,
                                     abv2offsetdict=NA_TIME_ZONE_ABRVS) ==
               timestroffset)


def test__normize_datetime_tmzone__with_offset_and_abv_cached_res():
    for _in, _out in NA_TIME_ZONE_CONVER_CACHED_RESs.items():
        assert(str(utils.normize_datetime_tmzone(_in)) == _out)


def test__normize_datetime_tmzone__with_abv_compare_to_cache():
    for abrv, offset in NA_TIME_ZONE_ABRVS.items():
        timestrabv = TIME_STRING1 + ' ' + abrv
        timestroffset = TIME_STRING1 + ' ' + offset
        offsetres = NA_TIME_ZONE_CONVER_CACHED_RESs[timestroffset]
        assert(str(utils.normize_datetime_tmzone(timestrabv)) == offsetres)


def test__normize_datetime_tmzone__str_with_no_tz():
    notzfunc = utils.if_no_tz_add_on_utc
    assert(str(utils.normize_datetime_tmzone(TIME_STRING1,
                                             handle_no_tz=notzfunc)))


if __name__ == '__main__':
    test__get_file_suffixes__1()
    test__get_file_suffixes__2()
    test__get_file_suffixes__3()
    test__get_file_suffixes__if_pathlib_is_installed()
    test___get_file_suffixes__opt_two__1()
    test___get_file_suffixes__opt_two__2()
    test___get_file_suffixes__opt_two__3()
    test__write_and_op_on_tmp()
    test__write_and_op_on_tmp__and__sopen()
    test__load_json()
    test__TZ_PAT_1()
    test__TZ_PAT_2()
    test__TZ_PAT_3()
    test__TZ_PAT_1__unicode()
    test__TZ_PAT_2__unicode()
    test__TZ_PAT_3__unicode()
    test__tz_abv_2_offset__test1()
    test__tz_abv_2_offset__test2()
    test__tz_abv_2_offset__test1_unicode()
    test__normize_datetime_tmzone__with_offset_and_abv_cached_res()
    test__normize_datetime_tmzone__with_abv_compare_to_cache()
    test__normize_datetime_tmzone__str_with_no_tz()
