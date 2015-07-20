# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/20/2015'

from tempfile import NamedTemporaryFile
import json
import re
from re import search

from arrow.parser import ParserError
from arrow import get


def sopen(uri, mode='rb', buffering=-1):
    return open(uri, mode=mode, buffering=buffering)


def load_file(uri, mode='rb', buffering=-1):
    with open(uri, mode=mode, buffering=buffering) as fp:
        return fp.read()


def load_json(uri):
    with sopen(uri) as fp:
        return json.load(fp)


def write_and_op_on_tmp(data, function, suffix, mode='w+b', tmpdir=None):
    with NamedTemporaryFile(suffix=suffix, mode=mode, dir=tmpdir) as tmp:
        tmp.file.write(data)
        tmp.file.seek(0)
        return function(tmp.name)


# ------------------------------------------------------------------------------
# Time Zone Normalization Functions.
NA_TIME_ZONE_ABRVS = {'EDT': '-0400',
                      'CST': '-0600',
                      'EST': '-0500',
                      'CDT': '-0500',
                      'MDT': '-0600',
                      'MST': '-0700',
                      'PDT': '-0700',
                      'PST': '-0800',
                      }


def tz_abv_2_offset(dtimestr, abv2offsetdict=NA_TIME_ZONE_ABRVS):
    res = dtimestr
    for abv, offset in abv2offsetdict.iteritems():
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
        return dtimestr + ' +00:00'
    else:
        return dtimestr


def normize_datetime_tmzone(dtimestr,
                            totmz='utc',
                            fmtstr='ddd, D MMM YYYY HH:mm:ss Z',
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
        if search(SINGLE_DIGIT_HOUR_PAT, res) and 'HH' in fmtstr:
            fmtstr = 'ddd, D MMM YYYY H:mm:ss Z'
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


normize_datetime_tmzone_north_am = normize_datetime_tmzone
_norm_dt_tz_na_docstr = ''.join(['\n\n! ! Deprecated ! !\n',
                                 'Use normize_datetime_tmzone!!\n\n',
                                 normize_datetime_tmzone.__doc__,
                                 ])
normize_datetime_tmzone_north_am.__doc__ = _norm_dt_tz_na_docstr

# ------------------------------------------------------------------------------
