# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'
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

import logging
LOG = logging.getLogger(__name__)

import sys
from functools import partial
from collections import(Mapping, Iterable)
import unicodedata

try:
    import cchardet as chardet
except(ImportError):
    import chardet
    LOG.debug('Using chardet. Install cchardet for increased speed.')
try:
    # optional but, ascii_only will not work
    from unidecode import unidecode
except(ImportError):
    LOG.debug('unidecode is not installed, normalization to ASCII will not be\
 as robust')
from ftfy import fix_text

from gentrify.utils import sopen

if sys.version_info[0] < 3:
    _STRINGTYPES = (basestring,)
else:
    # temp fix, so that 2.7 support wont break
    unicode = str  # adjusting to python3
    _STRINGTYPES = (str, bytes)


def verify_unicode(text):
    """
    Checks if text is unicode, if it's not, an error is raised.
    """
    if not isinstance(text, unicode):
        if isinstance(text, bytes):
            raise TypeError('Input text should be a unicode string, not byte.')
        else:
            raise TypeError('Input should be a unicode string.' +
                            ' It was not even text.')


# ----------------------------------------------------------------------------
# Cleaning up text.
def __fix_bad_escapes(text):
    """
    Fixes escaped characters that for what ever reason are not implemented
    correctly.

    Expects unicode text.
    """
    verify_unicode(text)
    text = text.replace(u'\\n', u'\n')
    text = text.replace(u'\\t', u'\t')
    text = text.replace(u'\\u', u'')
    return text


def __replace_misc_text_bits(text):
    """
    Replaces misc parts of text that do not belong.
    ex.
        '\\r' - (had to escape the backslash) Carriage returns that do not
                belong in everyday text (at least not on Linux), common in text
                comming from Windows.

    Expects unicode text.
    """
    verify_unicode(text)
    ftext = text
    ftext = ftext.replace(u'\r', u'')
    ftext = ftext.replace(u'\f', u' ')
    # Might not be necessary. Need to test.
    # ftext = ftext.replace(u"\u2019", u"'")  # Handles windows other single
    #                                         # quote.
    return ftext


def test_ascii(text):
    try:
        if isinstance(text, unicode):
            txt = text
        else:
            # using bytes on text to ensure that text is text
            txt = bytes(text).decode(encoding='ascii', errors='strict')
        txt = txt.encode('ascii', errors='strict')
        return True
    except(UnicodeEncodeError):
        return False


def ascii_only(text, errors='strict'):
    """
    Expects text to be Unicode.
    Returns ASCII encoded text.

    text - The text to be normalized to ASCII only.
    errors - 'strict' - Set the desired error handling scheme. Read the std
                        libraries codecs module docs for more info.
                        Possible: 'strict', 'replace', 'ignore',
                                  'xmlcharrefreplace', 'backslashreplace'
    """
    verify_unicode(text)
    try:
        asciitext = text.encode('ascii', errors=errors)
        if test_ascii(asciitext):
            return asciitext
    except UnicodeEncodeError as e:
        _except = e
    try:
        try:
            asciitext = unidecode(text)
            if test_ascii(asciitext):
                return asciitext
        except NameError:
            LOG.warning('Install unidecode to make ascii_only more robust.')
    except UnicodeEncodeError as e:
        _except = e
    _except.reason = ''.join([_except.reason,
                              ' -- ascii_only not able to change',
                              'text to ASCII only',
                              ])
    raise _except


def normize_text(text, asciionly=False):
    """
    Normalizes characters and converts all to
    best matching ASCII representation.

    Expects text to be Unicode.

    """
    verify_unicode(text)  # Raises an error if not Unicode.
    ntext = fix_text(text)
    ntext = unicodedata.normalize('NFD', ntext)
    ntext = __replace_misc_text_bits(ntext)
    ntext = __fix_bad_escapes(ntext)
    if asciionly:
        ntext = ascii_only(ntext)
    if not isinstance(ntext, unicode):
        # using bytes on ntext to ensure that ntext is text
        ntext = bytes(ntext).decode()
    return ntext


def sane_unicode(text, encoding='utf-8', errors='strict',
                 returnencoding=False, normize=False, clean=True,
                 asciionly=False):
    """
    Returns the Unicode representation of text.

    If returnencoding is True a tuple is returned otherwise just a string.

    text - The text to be decoded.
    encoding - 'utf-8' - The encoding of the text.
    errors - 'strict' - Set the desired error handling scheme. Read the std
                        libraries codecs module docs for more info.
                        Possible: 'strict', 'replace', 'ignore',
                                  'xmlcharrefreplace', 'backslashreplace'
    returnencoding - False - If True, it will also return the texts original
                             encoding.
    clean - True  - Cleans it, fixes past decode/encode mistakes, standardizes
                      the Unicode scheme.
    normize - False - Normalizes the Unicode text. Does everything clean does
                      but more aggressively.
    asciionly - False - Replaces all non-ASCII characters with closest ASCII
                        alternative. normize must also be true for this to run.

    If normize is set to True then the text will be cleaned even if clean is set
    to False, because cleaning is part of the normalization process.
    """
    if isinstance(text, unicode):
        unitext = text
        encdng = 'unicode'
    else:
        # Using bytes on ntext to ensure that ntext is text
        txt = bytes(text)
        try:
            # Best possible scenario. If the strictest mode doesn't work, let
            # chardet guess at the encoding (in case the provided is incorrect)
            # and use the user provided method of handling errors.
            unitext = bytes(txt).decode(encoding=encoding, errors="strict")
            encdng = encoding
        except(UnicodeDecodeError, LookupError):
            detection = chardet.detect(txt)
            encdng = detection.get('encoding')
            unitext = bytes(txt).decode(encoding=encdng, errors=errors)
    if normize:
        unitext = normize_text(unitext, asciionly=asciionly)
    elif clean:
        unitext = fix_text(unitext)
    if not isinstance(unitext, unicode):
        unitext = bytes(unitext).decode(encoding)
    if returnencoding:
        return unitext, encdng
    else:
        return unitext


def __insane_unicode(text):
    """
    !! Use as last resort!!
    Returns the Unicode representation of text.

    !! Should not be used directly, can really mess text up. !!
    If this can't decode the text, then the text really should be inspected
    more closely as it might not even be text.

    !!
    Even if this decodes the text, you may still experience further issues
    relating to encoding, while operating on the text.
    !!
    """
    try:
        unitext = sane_unicode(text)
        u'null' + unitext   # Sometimes the text still has issues after
        #                   # decoding. This helps check for potential
        #                   # issues.
        return unitext
    except(UnicodeDecodeError, UnicodeError):
        # obj is byte string
        btext = text.encode('string_escape')
        return __insane_unicode(btext)


def __insane_str(text, encoding='utf-8'):
    """
    Encodes text using the codec registered for encoding.
    !! Use as last resort!!
    """
    try:
        return text.encode(encoding)
    except UnicodeEncodeError:
        return __insane_unicode(text.encode('unicode_escape')).encode(encoding)


def make_unicode_dang_it(text,
                         encoding='utf-8',
                         errors='replace',
                         normize=False,
                         asciionly=False,
                         returnencoding=False,
                         insureencode=False):
    """
    Make text unicode Hell or High Water.

    +  normize: False - if True, normalizes the unicode characters.
    +  asciionly: False - if True changes all characters to their closest
            ASCII representation. Only applies if normize is True.
    +  insureencode: False - if 'True' will test if the text can be re-encoded.

    If this can't decode the text, then the text really should be inspected
    more closely as it might not even be text.

    !!
    Even if this decodes the text, you may still experience further issues
    relating to encoding, while operating on the text.
    !!
    """
    try:
        uni, encoding = sane_unicode(text,
                                     encoding=encoding,
                                     errors=errors,
                                     returnencoding=True,
                                     normize=normize,
                                     asciionly=asciionly)
    except(UnicodeDecodeError):
        return make_unicode_dang_it(__insane_unicode(text),
                                    encoding=encoding,
                                    errors=errors,
                                    returnencoding=returnencoding,
                                    normize=normize,
                                    asciionly=asciionly,
                                    insureencode=insureencode)
    if insureencode:
        try:
            uni = uni.encode('utf-8').decode(encoding='utf-8', errors='replace')
        except(UnicodeDecodeError):
            uni = __insane_unicode(__insane_str(uni, encoding='utf-8'))
    if returnencoding:
        return uni, encoding
    else:
        return uni


def auto_eng_unicode_dang_it(text,
                             encoding='utf-8',
                             errors='replace',
                             returnencoding=False):
    """
    Decode text, Hell or High Water.

    Same as make_unicode_dang_it, but with defaults that are better suited for
    automation.

    If this can't decode the text, then the text really should be inspected
    more closely as it might not even be text.

    !!
    Even if this decodes the text, you may still experience further issues
    relating to encoding, while operating on the text.
    !!
    """
    if isinstance(text, _STRINGTYPES):
        return make_unicode_dang_it(text,
                                    encoding,
                                    errors,
                                    normize=True,
                                    asciionly=True,
                                    returnencoding=returnencoding,
                                    insureencode=True)
    else:
        raise ValueError


auto_unicode_dang_it = auto_eng_unicode_dang_it


def make_byte(text, errors='strict', hohw=False, normize=False, asciionly=False,
              encoding='utf-8'):
    """
    Used for both changing a byte stings encoding and for changing a unicode
    string to byte.

    Default output encoding is UTF-8.

    hohw : Hell or High Water mode
    """
    if hohw:
        unitext = auto_eng_unicode_dang_it(text,
                                           encoding='utf-8',
                                           errors='replace')
    elif normize or asciionly:
        if asciionly and not normize:
            normize = True
        unitext = sane_unicode(text, encoding='utf-8', errors=errors,
                               normize=normize, asciionly=asciionly)
    else:
        unitext = text
    try:
        return unitext.encode(encoding, errors=errors)
    except(UnicodeDecodeError):
        return __insane_str(unitext)


def auto_normize_byte(text, encoding='utf-8', errors='replace'):
    return make_byte(text, errors='replace', hohw=True, encoding=encoding)


def convert_datastruct_text(data, convertfunc=unicode):
    convert_ds_text = partial(convert_datastruct_text,
                              convertfunc=convertfunc)
    if isinstance(data, _STRINGTYPES):
        return convertfunc(data)
    elif isinstance(data, Mapping):
        return dict(map(convert_ds_text, data.items()))
    elif isinstance(data, Iterable):
        return type(data)(map(convert_ds_text, data))
    else:
        return data

convert_datastruct_text_uni = partial(convert_datastruct_text,
                                      convertfunc=sane_unicode)
convert_datastruct_text_str = partial(convert_datastruct_text,
                                      convertfunc=make_byte)


def open_to_unicode(uri):
    """
    Made for py3.
    """
    try:
        with sopen(uri, mode='r') as fp:
            return fp.read()
    except UnicodeDecodeError:
        with sopen(uri, mode='r+b') as fp:
            return sane_unicode(fp.read())
