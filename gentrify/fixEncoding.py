# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'

import unicodedata
import logging
LOG = logging.getLogger(__name__)

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
from ftfy.fixes import remove_control_chars, remove_unsafe_private_use


def verify_unicode(text):
    """
    Checks if text is unicode, if it's not, an error is raised.
    """
    if not isinstance(text, unicode):
        if isinstance(text, str):
            raise TypeError('Input text should be a unicode string, not byte.')
        else:
            raise TypeError('Input should be a unicode string.' +
                            ' It was not even text.')


# ----------------------------------------------------------------------------
# Cleaning up text.

# all of this is done by fix_text by default.
def render_safe(text):
    '''
    Make sure the given text is safe to pass to an external process.
    '''
    return remove_control_chars(remove_unsafe_private_use(text))


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
        unicode(text,
                'ascii',
                errors='strict').encode('ascii', errors='strict')
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
    except UnicodeEncodeError, e:
        _except = e
    try:
        try:
            asciitext = unidecode(text)
            if test_ascii(asciitext):
                return asciitext
        except NameError:
            LOG.warning('Install unidecode to make ascii_only more robust.')
    except UnicodeEncodeError, e:
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
        encoding = 'unicode'
    else:
        try:
            # Best possible scenario. If the strictest mode doesn't work, let
            # chardet guess at the encoding (in case the provided is incorrect)
            # and use the user provided method of handling errors.
            unitext = unicode(text, encoding, errors="strict")
        except(UnicodeDecodeError, LookupError):
            detection = chardet.detect(text)
            encoding = detection.get('encoding')
            unitext = unicode(text, encoding, errors=errors)
    if normize:
        unitext = normize_text(unitext, asciionly=asciionly)
    elif clean:
        unitext = fix_text(unitext)
    if returnencoding:
        return unitext, encoding
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

    +  normize: if True, normalizes the unicode characters.
    +  asciionly: if True changes all characters to their closest
            ASCII representation. Only applies if normize is True.

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
    except UnicodeDecodeError:
        return make_unicode_dang_it(__insane_unicode(text),
                                    encoding=encoding,
                                    errors=errors,
                                    returnencoding=returnencoding,
                                    normize=normize,
                                    asciionly=asciionly,
                                    insureencode=insureencode)
    if insureencode:
        try:
            uni = unicode(uni.encode('utf-8'), 'utf-8', errors='replace')
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
    if isinstance(text, unicode) or isinstance(text, str):
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
    try:
        return unitext.encode(encoding, errors=errors)
    except(UnicodeDecodeError):
        return __insane_str(unitext)


def auto_normize_byte(text, encoding='utf-8', errors='replace'):
    return make_byte(text, errors='replace', hohw=True, encoding=encoding)
