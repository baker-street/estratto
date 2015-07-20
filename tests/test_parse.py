# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '7/19/2015'

import os
import json

from gentrify import(parse, utils)

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
    cached = utils.load_file('sample_parsed_email.json')
    new = json.dumps(parse.parse_multi_layer_file('sample_enron_email.'),
                     indent=4)
    assert(new == cached)
