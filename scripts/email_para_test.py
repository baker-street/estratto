#!/usr/bin/env python
# -*- coding: utf-8 -*-
__title__ = 'ellis_island'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/21/2015'

import sys
import random
import os
from uuid import uuid4
from gensim.utils import simple_preprocess
from chevy.utils import dir_spelunker as dirs

# from gentrify.parseEmail import email_whole_parse
from ellis_island import parallel_easy as para
from ellis_island.utils import Serial
from gentrify.parse import parse_multi_layer_file
from gentrify.parse import OKEXT


def parse_and_log(fname):
    try:
        parseddoc = parse_multi_layer_file(fname)
        for h in parseddoc:
            y = simple_preprocess(h['content']['body'])
            # continue
        return parseddoc
    except:
        with open('/home/steven_c/projects/ellis_island/eml_errors.log.' +
                  str(os.getpid()), 'a') as log:
            log.write(fname + '\n')
        return None


def main(k, dirroot='/mnt/data1/enron/enron_mail_20110402/textonly/enron/'):
    emaillist = [e for e in
                 dirs.spelunker_gen(dirroot)]
    print len(emaillist)
    if not k:
        k = len(emaillist)
    emlsmpl = [emaillist[random.randint(0, len(emaillist) - 1)]
               for i in xrange(k)]
    errorcount = 0
    resultiter = para.imap_easy(parse_and_log, emlsmpl, 5, 500, False)
    for i, res in enumerate(resultiter):
        if res is None:
            print 'ERROR!!!!!!!!11'
            errorcount += 1
        else:
            for n, doc in enumerate(res):
                ext = '.' + doc['filename'].split('.')[-1]
                newfname = '/mnt/data1/Case2/parsed/' + str(uuid4()) + ext
                doc.pop('rawbody', None)
                if doc['filename'].lower().endswith(tuple(OKEXT)):
                    Serial().json_save(doc, newfname, 4)
                print '\t', i, '\t', n, '\t', doc['filename']

        print 'ERRORCount:\t', errorcount


if __name__ == '__main__':
    try:
        k = int(sys.argv[1])
    except(IndexError):
        k = 0
    try:
        d = sys.argv[2]
    except(IndexError):
        d = '/mnt/data1/enron/enron_mail_20110402/textonly/enron/'
    main(k, d)
