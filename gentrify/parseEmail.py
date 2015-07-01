# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/20/2015'


from email.parser import Parser
from email.Header import decode_header
from email.utils import parseaddr

from base64 import b64decode

from re import(search,
               IGNORECASE,
               match,
               )

# from tempfile import NamedTemporaryFile
from smart_open import smart_open

from gentrify.fixEncoding import auto_unicode_dang_it
from gentrify.utils import normize_datetime_tmzone_north_am
# from gentrify.parseBinary import parse_binary_from_string
# from gentrify.parse import parse_multi_layer_file
# from gentrify.parse import get_attchs_text

import logging
LOG = logging.getLogger(__name__)


EMAILEXTS = set(['.eml',
                 '.txt',
                 '.email',
                 ])

EXTRA_HEADERS = ['thread-index',
                 'message-id',
                 'return-path',
                 ]
EXTRA_ADDRESS_HEADERS = ['to',
                         'bcc',
                         'cc',
                         ]


# ----------------------------------------------------------------------------
# Basic email parsing
def email_parse_attachment(msgpart):
    content_disposition = msgpart.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and
                dispositions[0].lower() == "attachment"):
            filedata = msgpart.get_payload()
            try:
                if 'base64' in msgpart.get('Content-Transfer-Encoding',
                                           None).lower():
                    filedata = b64decode(filedata)
            except(AttributeError, TypeError):
                return None
            fname = auto_unicode_dang_it(msgpart.get_filename())
            if match('(Untitled)(.{0,3})(attachment)(.{0,10})(\.txt)', fname):
                filedata = u''

            attachment = {'body': filedata,
                          'type': msgpart.get_content_type(),
                          'filename': fname,
                          }
            for param in dispositions[1:]:
                name, value = param.split("=")
                name = name.strip().lower()
                if name == "filename":
                    attachment['filename'] = value.replace('"', '')
            return attachment
    return None


def attch_stats_from_attchdict(attchdict):
    attchfnamlist = [attch['filename'] for attch in attchdict]
    simpleattchdict = dict()
    simpleattchdict['filename'] = attchfnamlist
    simpleattchdict['number_of_attachments'] = len(attchfnamlist)
    return simpleattchdict


def email_parse(content,
                extraheaders=EXTRA_HEADERS,
                extraaddress_headers=EXTRA_ADDRESS_HEADERS):
    """
    Returns unicode.

    Converts 'Date' to UTC.
    """
    p = Parser()
    msgobj = p.parsestr(content)
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
        msgbits = {'subject': auto_unicode_dang_it(subject),
                   'body': body_text,
                   # 'body_html': body_html,
                   'from': tuple([auto_unicode_dang_it(addr)
                                  for addr in parseaddr(msgobj.get('From'))
                                  ]),
                   'attachment': attch_stats_from_attchdict(attachments),
                   'date': unicode(normize_datetime_tmzone_north_am(
                                   msgobj['date'])),
                   }
    except ValueError:
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
            except(KeyError, AttributeError):
                msgbits[field] = u''
    return msgbits, attachments


# ----------------------------------------------------------------------------
# Testing for emails
def is_an_email_from_cont(txt):
    """
    Tests if a string is an email (mime data structure) by checking if the
    string contains:
        Mime-Version:
        From:
        Subject:
    """
    return bool(search('Mime-Version\:', txt, flags=IGNORECASE) and
                search('From\:', txt, flags=IGNORECASE) and
                search('Subject\:', txt, flags=IGNORECASE))


def is_an_email_from_ext(fname, extset=EMAILEXTS):
    """
    Tests if a file is an email based on the files extension.
    This is only a rough guess and should be combined with other
    methods.

    Extensions in extset, should be lower case.
    """
    return fname.lower().endswith(tuple(extset))


def is_an_email(fname, txt=None, extset=EMAILEXTS):
    """
    Tests if a file is and email.
    First using the files extension using the extensions in extset.
    Next using the contents of the file (txt).
    If txt (the contents) is not supplied the function will load the file.
    """
    if not is_an_email_from_ext(fname, extset):
        return False
    else:
        if txt is None:
            with open(fname) as fobj:
                txt = fobj.read()
    return is_an_email_from_cont(txt)


# ----------------------------------------------------------------------------
# parse attachments
"""
def get_attchs_text(rawattchslist):
    attchslist = []
    for i, attch in enumerate(rawattchslist):
        parsedfile = parse_multi_layer_file(uri=attch['body'],
                                            txt=attch['filename'],
                                            ftype=attch['type'])
        for parseddoc in parsedfile:
            attchslist.append(parseddoc)
    return attchslist
"""


# ----------------------------------------------------------------------------
# parse email and attachments
def email_whole_parse_from_str(text):
    """
    Parses email from string and its attachments.
    Returns attachments as both raw and plain text (if possible).
    """
    emailtuple = email_parse(text)
    parsedemaillist = [emailtuple[0]]
    parsedemaillist.extend(emailtuple[1])
    return parsedemaillist


def email_whole_parse(uri, txt=None, returnraw=False):
    """
    Parses email from file and its attachments.
    Returns attachments as both raw and plain text (if possible).

    Can handle s3 and HDFS.
    """
    if txt is None:
        with smart_open(uri) as fobj:
            txt = fobj.read()
    emailtuple = email_whole_parse_from_str(txt)
    emailtuple[0]['filename'] = auto_unicode_dang_it(uri)
    if returnraw:
        return emailtuple, txt
    else:
        return emailtuple
