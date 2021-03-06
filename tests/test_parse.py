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


import sys
import os
from os.path import join
import json

# import pytest

from estratto import(parse, utils)
from estratto.utils import flatten_handle_all

if sys.version_info[0] >= 3:
    unicode = str  # adjusting to python3
    _STRINGTYPES = (str, bytes)
else:
    _STRINGTYPES = (basestring,)

TESTDIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TESTDIR)


def test__fit_into_data_mold():
    smpl = {u'content': 'parsedtextparsedtextparsedtextparsedtextparsedtext',
            u'filename': 'uriuriuriuriuriuriuriuriuriuri',
            u'info': 'infoinfoinfoinfoinfoinfoinfoinfoinfoinfo',
            u'mime': 'mimemimemime',
            u'rawbody': 'txttxttxttxttxttxttxttxttxttxt',
            u'type': 'ftypeftypeftype',
            }
    output = parse.fit_into_data_mold('parsedtext'*5,
                                      'txt'*10,
                                      'uri'*10,
                                      'ftype'*3,
                                      'mime'*3,
                                      'info'*10)
    assert(smpl == output)


def test__parse_multi_layer_file():
    cached = utils.load_json(join(TESTDIR, 'sample_parsed_email.json'),
                             mode='r')
    prsd = parse.parse_multi_layer_file('sample_enron_email.')
    new = json.loads(json.dumps(prsd))
    assert(new[0]['content']['body'] == cached[0]['content']['body'])


def test__parse_multi_layer_file__is_output_all_unicode():
    doclist = parse.parse_multi_layer_file(join(TESTDIR,
                                                'sample_enron_email.'))
    for docdict in doclist:
        docdict['content']['attachment']['filename'] = u''
        docdict['rawbody'] = u''
        for item in flatten_handle_all(docdict, dictvalues=True):
            if isinstance(item, _STRINGTYPES):
                assert(isinstance(item, unicode))


MINIEMLWithAttch = ('testdata/The_Adventures_of_Sherlock_Holmes/' +
                    'from_gmail_and_libre_office/mini/' +
                    'pg1661-mini_with-attch.eml')


def test__parse_large_email_with_large_mix_of_files():
    doclist = parse.parse_multi_layer_file(MINIEMLWithAttch)
    for prt in doclist:
        if utils.file_exts(prt['filename']).lower() in parse.OKEXT:
            assert(20 < len(prt['content']['body']))


if __name__ == '__main__':
    test__fit_into_data_mold()
    test__parse_multi_layer_file()
    test__parse_multi_layer_file__is_output_all_unicode()
    test__parse_large_email_with_large_mix_of_files()
