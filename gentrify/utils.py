# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/20/2015'


from tempfile import NamedTemporaryFile
import json
import re

import arrow


def load_json(filepath):
    with open(filepath) as fp:
        return json.load(fp)


def write_and_op_on_tmp(data, function, suffix, mode='w+b', dir=None):
    with NamedTemporaryFile(suffix=suffix, mode=mode, dir=dir) as tmp:
        tmp.file.write(data)
        tmp.file.seek(0)
        return function(tmp.name)


def normize_datetime_tmzone_north_am(s, totmz='utc'):
    """
    Pattern:
        ddd, D MMM YYYY HH:mm:ss
    Likes (ex):
        Sat, 20 Jun 2015 09:15:18 -0700
    Will put up with (ex):
        Sat, 20 Jun 2015 09:15:18 MST
    """
    try:
        return arrow.get(s, 'ddd, D MMM YYYY HH:mm:ss Z').to(totmz)
    except(arrow.arrow.parser.ParserError):
        try:
            return arrow.get(s, 'ddd, D MMM YYYY H:mm:ss Z').to(totmz)
        except(arrow.arrow.parser.ParserError):
            s = re.sub('EDT', '-0400', s, flags=re.IGNORECASE)
            s = re.sub('CST', '-0600', s, flags=re.IGNORECASE)
            s = re.sub('EST', '-0500', s, flags=re.IGNORECASE)
            s = re.sub('CDT', '-0500', s, flags=re.IGNORECASE)
            s = re.sub('MDT', '-0600', s, flags=re.IGNORECASE)
            s = re.sub('MST', '-0700', s, flags=re.IGNORECASE)
            s = re.sub('PDT', '-0700', s, flags=re.IGNORECASE)
            s = re.sub('PST', '-0800', s, flags=re.IGNORECASE)
            return arrow.get(s, 'ddd, D MMM YYYY HH:mm:ss Z').to(totmz)
