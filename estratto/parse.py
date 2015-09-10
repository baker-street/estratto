# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.e.cutting@linux.com'
__created_on__ = '6/23/2015'
__copyright__ = "estratto  Copyright (C) 2015  Steven Cutting"
__license__ = "AGPL"
from . import(__title__, __version__, __credits__, __maintainer__, __email__,
              __status__)
__title__
__version__
__credits__
__maintainer__
__email__
__status__


from os.path import dirname

from magic import from_buffer
from types import NoneType


# TODO (steven_c) Replace smart_open!
# TODO (steven_c) Replace smart_open!

from estratto.fixEncoding import(auto_unicode_dang_it, sane_unicode)
from estratto.parseBinary import parse_binary
# from estratto.fixEncoding import make_unicode_dang_it
from estratto.parseEmail import(is_an_email,
                                email_whole_parse)
from estratto import utils

CONFFILE = dirname(utils.__file__) + '/defconf.json'
OKEXT = set(utils.load_json(CONFFILE, mode='r')['ok_ext_set'])


def get_file_info_from_buffer(txt):  # Consider putting in utils
    info = sane_unicode(from_buffer(txt))
    mime = sane_unicode(from_buffer(txt, True))
    ftype = sane_unicode(mime.split(u'/')[-1])
    return info, mime, ftype  # Consider using a namedtuple.


def fit_into_data_mold(parseddict, txt, uri, ftype, mime, info):
    return {u'content': parseddict,
            u'rawbody': txt,
            u'filename': uri,
            u'type': ftype,
            u'mime': mime,
            u'info': info,
            }


# TODO Add support for zip files and more than one generation
# TODO (steven_c) Rewrite this so that it sucks less.
#   - Less complex
#   - More readable
def parse_multi_layer_file(uri, txt=None, ftype=None, okext=OKEXT):
    """
    Can handle files that contain files, e.g. emails with attachments.
    Returns a list with parsed files each in a dict tree.

        type: is ether the extension or a set definition, e.g. email.
    """
    if isinstance(txt, NoneType):
        with open(uri) as fogj:
            txt = fogj.read()
    if is_an_email(uri, text=txt):
        parsedtxtlist = email_whole_parse(uri=uri,
                                          text=txt)
        info, mime, ftype = get_file_info_from_buffer(txt)
        for i, parsedtxt in enumerate(parsedtxtlist):
            if i == 0:
                # the zero gen file does not return with a file name
                parsedtxt['filename'] = uri
                emlparsed = [(fit_into_data_mold(parseddict=parsedtxt,
                                                 txt=txt,
                                                 uri=auto_unicode_dang_it(uri),
                                                 ftype=u'email',
                                                 mime=mime,
                                                 info=info))]
            else:
                attchtxt = parsedtxt['body']
                if not attchtxt:
                    attchtxt = u''
                info, mime, ftype = get_file_info_from_buffer(attchtxt)
                fname = parsedtxt['filename']
                for parsedbit in parse_multi_layer_file(uri=fname,
                                                        txt=attchtxt,
                                                        ftype=ftype,
                                                        okext=okext):
                    emlparsed.append(parsedbit)
        return emlparsed
    parsedtxt = parse_binary(string=txt,
                             fname=uri)
    if not ftype:
        ftype = uri.split('.')[-1]
    if not parsedtxt:
        parseddict = {u'body': u''}
    else:
        parseddict = {u'body': parsedtxt}
    info, mime, ftype = get_file_info_from_buffer(txt)
    parseddict[u'filename'] = sane_unicode(uri)
    return [fit_into_data_mold(parseddict=parseddict,
                               txt=txt,
                               uri=uri,
                               ftype=ftype,
                               mime=mime,
                               info=info)]
