# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'

import os
import json

from gentrify import(parse, utils)
from gentrify.utils import flatten_handle_all

TEST_DIR = '/'.join(__file__.split('/')[:-1]) + '/'
os.chdir(TEST_DIR)


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
    cached = utils.load_json('sample_parsed_email.json')
    new = json.loads(json.dumps(
                     parse.parse_multi_layer_file('sample_enron_email.')))
    assert(new == cached)


def test__parse_multi_layer_file__is_output_all_unicode():
    doclist = parse.parse_multi_layer_file('sample_enron_email.')
    for docdict in doclist:
        # These items should not be decoded, so omitting them from the test.
        docdict['content']['attachment']['filename'] = u''
        docdict['rawbody'] = u''
        for item in flatten_handle_all(docdict, dictvalues=True):
            if isinstance(item, basestring):
                assert(isinstance(item, unicode))
