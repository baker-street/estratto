# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/20/2015'
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


import logging
LOG = logging.getLogger(__name__)

import sys
from tempfile import NamedTemporaryFile
import json
import re
from re import search
from collections import Iterable

from arrow.parser import ParserError
from arrow import get

if sys.version_info[0] < 3:
    _STRINGTYPES = (basestring,)
else:
    # temp fix, so that 2.7 support wont break
    unicode = str  # adjusting to python3
    _STRINGTYPES = (str, bytes)

# ------------------------------------------------------------------------------
# Keep this stuff together. Doing it this way so both versions can be
# easily tested.
GETFILESUFDOCSTR_pt1 = """
    Parses file extension from file name.
    Ex:
        '/foo/bar/baz.txt' returns '.txt'
"""
from os.path import splitext


def _get_file_suffixes(filepath):
    """
        '/foo/bar/baz.tar.gz' returns '.gz'
    For it to work with stacked extensions install pathlib.
    Ex with pathlib installed:
        '/foo/bar/baz.tar.gz' returns '.tar.gz'
    """
    return splitext(filepath)[-1]
try:
    from pathlib import Path

    def get_file_suffixes(filepath):
        """
        '/foo/bar/baz.tar.gz' returns '.tar.gz'
        """
        return ''.join(Path(filepath).suffixes)
except ImportError:
    LOG.debug('pathlib is not installed. Install for better path parsing.')
    get_file_suffixes = _get_file_suffixes
    get_file_suffixes.__doc__ = GETFILESUFDOCSTR_pt1 + get_file_suffixes.__doc__
# ------------------------------------------------------------------------------


def sopen(uri, mode='r', buffering=-1):
    return open(uri, mode=mode, buffering=buffering)


def load_file(uri, mode='r', buffering=-1):
    with open(uri, mode=mode, buffering=buffering) as fp:
        return fp.read()


def load_json(uri, mode='r'):
    with open(uri, mode=mode) as fp:
        return json.load(fp)


def write_and_op_on_tmp(data, function, suffix, mode='w', tmpdir=None,
                        **kwargs):
    with NamedTemporaryFile(suffix=suffix, mode=mode, dir=tmpdir,
                            **kwargs) as tmp:
        tmp.write(data)
        tmp.seek(0)
        return function(tmp.name)


# Try to make the flatten funcs suck a little less; too many loops and what not.
def flatten_dict_tree(dicttree, __keypath=u''):
    """
    Flattens only the dicts in a dict tree.
    """
    newdict = {}
    for key, value in dicttree.items():
        fullkeypath = __keypath + '-' + key
        if isinstance(value, dict):
            newdict.update(flatten_dict_tree(value, fullkeypath))
        else:
            newdict[key] = value
    return newdict


def flatten_array_like_strct_gen(arraything, dictvalues=False):
    for i in arraything:
        if isinstance(i, _STRINGTYPES):
            yield i
        elif isinstance(i, dict):
            if dictvalues:
                g = flatten_array_like_strct_gen(flatten_dict_tree(i).values(),
                                                 dictvalues=dictvalues)
                for j in g:
                    yield j
            else:
                yield i
        elif isinstance(i, Iterable):
            for j in flatten_array_like_strct_gen(i,
                                                  dictvalues=dictvalues):
                yield j
        else:
            yield i


def flatten_handle_all(datastrct, dictvalues=False):
    if isinstance(datastrct, dict):
        if not dictvalues:
            yield datastrct
        else:
            for i in flatten_array_like_strct_gen(datastrct.values(),
                                                  dictvalues=dictvalues):
                yield i
    else:
        for i in flatten_array_like_strct_gen(datastrct,
                                              dictvalues=dictvalues):
            yield i

# ------------------------------------------------------------------------------
# Time Zone Normalization Functions.
NA_TIME_ZONE_ABRVS = {u'EDT': u'-0400',
                      u'CST': u'-0600',
                      u'EST': u'-0500',
                      u'CDT': u'-0500',
                      u'MDT': u'-0600',
                      u'MST': u'-0700',
                      u'PDT': u'-0700',
                      u'PST': u'-0800',
                      }


def tz_abv_2_offset(dtimestr, abv2offsetdict=NA_TIME_ZONE_ABRVS):
    res = dtimestr
    for abv, offset in abv2offsetdict.items():
        res = re.sub(abv, offset, res, flags=re.IGNORECASE)
    return res


TZ_PAT_1 = re.compile(r"(\s)([0-9]{1,2})(\:)([0-9]{2})(\:)([0-9]{2})" +
                      r"(.+)([\-\+])([0-9]{1,2})(\:)([0-9]{2})$"
                      )
TZ_PAT_2 = re.compile(r"(\s)([0-9]{1,2})(\:)([0-9]{2})(\:)([0-9]{2})" +
                      r"(.+)([\-\+])([0-9]{4})$"
                      )
TZ_PAT_3 = re.compile(r"(\s)([0-9]{1,2})(\:)([0-9]{2})(\:)([0-9]{2})" +
                      r"(\s{1})([A-Z]{1,5})$"
                      )
TZ_PATS = [TZ_PAT_1,
           TZ_PAT_2,
           TZ_PAT_3,
           ]


def test_for_tz(dtimestr):  # , flags=0):
    # if isinstance(dtimestr, unicode):
    #     flags = UNICODE
    res = False
    for tzpat in TZ_PATS:
        if search(tzpat, dtimestr):  # , flags=flags):
            res = True
    return res


NO_TZ_PAT = re.compile(r"(\s)([0-9]{1,2})(\:)([0-9]{2})(\:)([0-9]{2})$")

SINGLE_DIGIT_HOUR_PAT = re.compile(r"(\s)([0-9]{1})(\:)([0-9]{2})(\:)([0-9]{2})"
                                   )


def if_no_tz_add_on_utc(dtimestr):
    if not test_for_tz(dtimestr):
        return dtimestr + u' +00:00'
    else:
        return dtimestr


def normize_datetime_tmzone(dtimestr,
                            totmz=u'utc',
                            fmtstr=u'ddd, D MMM YYYY HH:mm:ss Z',
                            tz_abv2offset=tz_abv_2_offset,
                            handle_no_tz=None):
    """
    Pattern:
        ddd, D MMM YYYY HH:mm:ss
    Likes (ex):
        Sat, 20 Jun 2015 09:15:18 -0700
    Will put up with (ex):
        Sat, 20 Jun 2015 09:15:18 MST
    """
    res = dtimestr
    try:
        return get(res, fmtstr).to(totmz)
    except(ParserError):
        if search(SINGLE_DIGIT_HOUR_PAT, res) and u'HH' in fmtstr:
            fmtstr = u'ddd, D MMM YYYY H:mm:ss Z'
        elif handle_no_tz and (not test_for_tz(res)):
            res = handle_no_tz(res)
        elif search(TZ_PAT_3, res):
            res = tz_abv2offset(res)
        else:
            raise ParserError('Could not parse\t' + dtimestr)
        return normize_datetime_tmzone(res,
                                       totmz=totmz,
                                       fmtstr=fmtstr,
                                       tz_abv2offset=tz_abv2offset,
                                       handle_no_tz=handle_no_tz)


normize_dtime_tmzn_nrth_am = normize_datetime_tmzone
_norm_dt_tz_na_docstr = ''.join(['\n\n! ! Deprecated ! !\n',
                                 'Use normize_datetime_tmzone!!\n\n',
                                 normize_datetime_tmzone.__doc__,
                                 ])
normize_dtime_tmzn_nrth_am.__doc__ = _norm_dt_tz_na_docstr

# ------------------------------------------------------------------------------
