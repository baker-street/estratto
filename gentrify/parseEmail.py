# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
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


# TODO (steven_c) Clean and optimize.
# TODO (steven_c) Make code more readable.

import logging
LOG = logging.getLogger(__name__)

import sys
from os.path import dirname
from email.parser import Parser
if sys.version_info[0] < 3:
    from email.Header import decode_header
else:
    from email.header import decode_header
from email.utils import parseaddr
from base64 import b64decode
from re import(search,
               IGNORECASE,
               match,
               )


from gentrify.fixEncoding import(auto_unicode_dang_it,
                                 sane_unicode,
                                 open_to_unicode)
from gentrify import utils
from gentrify.utils import normize_dtime_tmzn_nrth_am

from gentrify.utils import sopen

CONFDICT = utils.load_json(dirname(utils.__file__) + '/defconf.json',
                           mode='r')
EMAILEXTS = set(CONFDICT['email_ext_set'])

EXTRA_HEADERS = CONFDICT['email_extra_headers']
EXTRA_ADDRESS_HEADERS = CONFDICT['email_extra_address_headers']

if sys.version_info[0] < 3:
    _STRINGTYPES = (basestring,)
else:
    unicode = str  # adjusting to python3
    _STRINGTYPES = (str, bytes)


# ----------------------------------------------------------------------------
# Basic email parsing
def atch_fname_from_dispositions(dispositions):
    for param in dispositions[1:]:
        try:
            label, name = param.split(b"=")
        except(ValueError):
            label, name, ext = param.split(b"=")
            name = name + ext
            if param:
                p = param
            else:
                p = b"Param==None"
            if name:
                v = name
            else:
                v = b"Name==None"
            if b"filename" in label:
                LOG.debug(b'EmailPath:\t' + p + '\t' + v)
        if b"filename" in label:
            name = auto_unicode_dang_it(name)
            name = name.strip().lower()
            name = name.strip(b'*').strip(b"utf-8''").replace(b'%20',
                                                              b' ').strip(b'"')
            return name


def email_parse_attachment(msgpart):  # TODO (steven_c) Make less complex.
    content_disposition = msgpart.get(b"Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(b";")
        if bool(content_disposition and
                dispositions[0].lower() == b"attachment"):
            filedata = msgpart.get_payload()
            try:
                if b'base64' in msgpart.get(b'Content-Transfer-Encoding',
                                            None).lower():
                    filedata = b64decode(filedata)
            except(AttributeError, TypeError):
                return None
            fname = auto_unicode_dang_it(msgpart.get_filename())
            if match(b'(Untitled)(.{0,3})(attachment)(.{0,10})(\.txt)', fname):
                filedata = u''

            attachment = {u'body': filedata,
                          u'type': msgpart.get_content_type(),
                          u'filename': fname,
                          # fyi, this is a filename not pointer.
                          }
            attachment[u'filename'] = atch_fname_from_dispositions(dispositions)
            return attachment
    return None


def attch_stats_from_attchdict(attchdict):
    attchfnamlist = [attch[u'filename'] for attch in attchdict]
    simpleattchdict = dict()
    simpleattchdict[u'filename'] = attchfnamlist
    simpleattchdict[u'number_of_attachments'] = len(attchfnamlist)
    return simpleattchdict


# TODO (steven_c) Make less complex.
def email_parse(content,
                extraheaders=EXTRA_HEADERS,
                extraaddress_headers=EXTRA_ADDRESS_HEADERS):
    """
    Returns unicode.

    Converts 'Date' to UTC.
    """
    p = Parser()
    msgobj = p.parsestr(str(content))
    if msgobj['Subject'] is not None:
        decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s, enc in decodefrag:
            if enc:
                s = auto_unicode_dang_it(s,
                                         enc)
            subj_fragments.append(s)
        subject = ''.join(subj_fragments)
    else:
        subject = u''
    attachments = []
    body_text = u""
    for part in msgobj.walk():
        attachment = email_parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            bodypayload = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if not charset:
                charset = 'utf-8'
            if bodypayload:
                body_text += auto_unicode_dang_it(bodypayload,
                                                  charset)
        elif (not body_text) and (part.get_content_type() == "text/html"):
            htmlpayload = part.get_payload(decode=True)
            if htmlpayload:
                body_text += auto_unicode_dang_it(htmlpayload,
                                                  part.get_content_charset(),
                                                  'replace')
    try:
        try:
            datetime = sane_unicode(normize_dtime_tmzn_nrth_am(msgobj['date']))
        except(TypeError):
            datetime = None
        msgbits = {u'subject': auto_unicode_dang_it(subject),
                   u'body': body_text,
                   # 'body_html': body_html,
                   u'from': tuple([auto_unicode_dang_it(addr)
                                   for addr in parseaddr(msgobj.get('From'))
                                   ]),
                   u'attachment': attch_stats_from_attchdict(attachments),
                   u'datetime': datetime,
                   }
    except ValueError:
        LOG.critical('Could not parse required headers')
        raise ValueError('Was not able to parse all required email headers.')
    if extraaddress_headers:
        for field in extraaddress_headers:
            try:
                msgbits[field] = tuple([tuple([auto_unicode_dang_it(person)
                                               for person in parseaddr(bit)])
                                        for bit in msgobj[field].split(',')
                                        ])
            except(KeyError, AttributeError):
                msgbits[field] = tuple([(u'', u'')])
    if extraheaders:
        for field in extraheaders:
            try:
                msgbits[field] = auto_unicode_dang_it(msgobj[field])
            except(KeyError, AttributeError, ValueError):
                msgbits[field] = u''
    return msgbits, attachments


# ----------------------------------------------------------------------------
# Testing for emails
def is_an_email_from_cont(text):
    """
    Tests if a string is an email (mime data structure) by checking if the
    string contains:
        Mime-Version:
        From:
        Subject:
    """
    if isinstance(text, _STRINGTYPES):
        if isinstance(text, unicode):
            txt = text.encode('utf-8')
        else:
            txt = text
        return bool(bool(search(b'Mime-Version\:', txt, flags=IGNORECASE)) and
                    bool(search(b'From\:', txt, flags=IGNORECASE)) and
                    bool(search(b'Subject\:', txt, flags=IGNORECASE)))
    else:
        raise TypeError("'text' is not text, it's not a string type. It is:\t" +
                        type(text))


def is_an_email_from_ext(fname, extset=EMAILEXTS):
    """
    Tests if a file is an email based on the files extension.
    This is only a rough guess and should be combined with other
    methods.

    Extensions in extset, should be lower case.
    """
    return fname.lower().endswith(tuple(extset))


def is_an_email(fname, text=None, extset=EMAILEXTS):
    """
    Tests if a file is and email.
    First using the files extension using the extensions in extset.
    Next using the contents of the file (text).
    If text (the contents) is not supplied the function will load the file.
    """
    if not is_an_email_from_ext(fname, extset):
        return False
    else:
        if text is None:
            with open(fname, 'r+b') as fobj:
                text = fobj.read()
    return is_an_email_from_cont(text)


# ----------------------------------------------------------------------------
# parse email and attachments
def email_whole_parse_from_str(text):
    """
    Parses email from string and its attachments.
    Returns attachments as both raw and plain text (if possible).
    """
    if not is_an_email_from_cont(text):
        raise TypeError('text does not contain an email.')
    emailtuple = email_parse(text)
    actulemail = emailtuple[0]
    actulemail[u'type'] = u'email'
    parsedemaillist = [actulemail]
    parsedemaillist.extend(emailtuple[1])  # adding on the attachments.
    return tuple(parsedemaillist)


def email_whole_parse(uri, text=None, returnraw=False):
    """
    Parses email from file and its attachments.
    Returns attachments as both raw and plain text (if possible).

    Not yet, but will handle s3 and HDFS.
    """
    if text is None:
        text = open_to_unicode(uri)
    emailtuple = email_whole_parse_from_str(text)
    emailtuple[0][u'filename'] = auto_unicode_dang_it(uri)
    if returnraw:
        return emailtuple, text
    else:
        return emailtuple
