#!/usr/bin/env python
# -*- coding: utf-8 -*-
__title__ = 'ellis_island'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/21/2015'

import sys
import random

from chevy.utils import dir_spelunker as dirs

from ellis_island.gentrify import parseEmail as pmail


def main(k, dirroot='/mnt/data1/enron/enron_mail_20110402/textonly/enron'):
    emaillist = [e for e in
                 dirs.spelunker_gen(dirroot)]
    print len(emaillist)
    if not k:
        k = len(emaillist)
    emlsmpl = [emaillist[random.randint(0, len(emaillist) - 1)]
               for i in xrange(k)]
    # logsize = (k * 10) / 100
    skipcount = 0
    with open('/home/steven_c/projects/ellis_island/eml_errors.log',
              'a') as log:
        for i, emlpath in enumerate(emlsmpl):
            print i, emlpath
            try:
                emldict = pmail.email_whole_parse(emlpath)
                # if not i % logsize:
                print '\t', str(len(emldict['attachments'])),
                print '\t', emldict['from'],
                print '\t', str(emldict['thread-index']), ' '
                p_atchs = emldict['pattachments']
                print '\tattachments:', len(p_atchs)
                for at in p_atchs.values():
                    print '\t\t', at['filename']
            except:
                skipcount += 1
                print 'SKIPPING!!!!!!!!!!!!!!!111'
                log.write(emlpath + '\n')
            print '\nskipcount: ', skipcount, '\n'

if __name__ == '__main__':
    try:
        k = int(sys.argv[1])
    except(IndexError):
        k = 0
    try:
        d = sys.argv[2]
    except(IndexError):
        d = '/mnt/data1/enron/enron_mail_20110402/textonly/enron'
    main(k, d)
