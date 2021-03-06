# -*- coding: utf-8 -*-
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'
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

import sys
import logging
LOG = logging.getLogger(__name__)

from os.path import dirname, isfile
import zipfile
from subprocess import Popen, PIPE
import re
from traceback import format_stack


# from xlrd import XLRDError
try:
    from docx import Document
except ImportError:
    LOG.warning("docx not installed, install to extract '.docx' text.")
try:
    from textract import process
    from textract.exceptions import(ExtensionNotSupported,
                                    ShellError)
except ImportError:
    LOG.warning('textract not installed, install for robust text extraction.')
# http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
try:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfdocument import(PDFTextExtractionNotAllowed,
                                     PSEOF,
                                     PDFEncryptionError,
                                     PDFSyntaxError)
except ImportError:
    LOG.warning('pdfminer not installed, install to extract PDF text.')
try:
    from bs4 import BeautifulSoup
except ImportError:
    LOG.warning('BeautifulSoup (bs4) is not installed,',
                'will not be able to parse XML and HTML.')


# ------------------------------------------------------------------------------
# Handle python3 conversion
if sys.version_info[0] < 3:
    from cStringIO import StringIO
    from os import devnull
    DEVNULL = open(devnull, 'wb')
else:
    from subprocess import DEVNULL
    from io import StringIO

from estratto.fixEncoding import auto_unicode_dang_it
from estratto import utils
from estratto.utils import(write_and_op_on_tmp,
                           get_file_suffixes,
                           guess_ext_from_mime)


CONFFILE = dirname(utils.__file__) + '/defconf.json'
OKEXT = set(utils.load_json(CONFFILE, mode='r')['ok_ext_set'])


def handle_zip_files(zippath, tmpdir):
    with zipfile.ZipFile(zippath) as daszip:
        namelist = daszip.namelist()
        for name in namelist:
            daszip.extract(name, path=tmpdir)
        return namelist


def auto_textract(filepath):
    """
    Use when failure is not an option.
    If an excetpion is raised by textract, u'' is returned.
    """
    try:
        try:
            t = process(filepath, language='nor')
            if t:
                return t
            else:
                return u''
        except NameError:
            LOG.warning('Attempted to use textract but, ' +
                        'textract not installed, install for ' +
                        'robust text extraction.')
            return u''
    except (ExtensionNotSupported,
            IndexError,
            ShellError,
            TypeError):
        return u''


class StringIOContext(object):
    def __init__(self):
        self.retstr = StringIO()

    def __enter__(self):
        return self.retstr

    def __exit__(self, *args):
        self.retstr.close()


class TextConverterContext(object):
    def __init__(self, rsrcmgr, retstr, codec, laparams):
        self.device = TextConverter(rsrcmgr,
                                    retstr,
                                    codec=codec,
                                    laparams=laparams)

    def __enter__(self):
        return self.device

    def __exit__(self, *args):
        self.device.close()


# TODO (steven_c) "convert_pdf_to_txt" Try and simplify this, maybe break it up.
def convert_pdf_to_txt(_path):
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()
    with StringIOContext() as retstr:
        with TextConverterContext(rsrcmgr,
                                  retstr,
                                  codec=codec,
                                  laparams=laparams) as device:
            with file(_path, 'rb') as fp:
                try:
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    password = ""
                    maxpages = 0
                    caching = True
                    pagenos = set()
                    for page in PDFPage.get_pages(fp,
                                                  pagenos,
                                                  maxpages=maxpages,
                                                  password=password,
                                                  caching=caching,
                                                  check_extractable=True):
                        try:
                            interpreter.process_page(page)
                        except AttributeError as e:
                            # TODO (steven_c) remove this and solve the prob.
                            LOG.error('\t'.join(['File:', _path,
                                                 'ErrMessage:', e.message,
                                                 'Traceback:', format_stack(),
                                                 ]))
                            continue
                    str_ = retstr.getvalue()
                    if str_:
                        return str_
                    else:
                        return u''
                except(TypeError):
                    return u''


def handle_pdf_files_pdfminer(filepath):
        try:
            try:
                return convert_pdf_to_txt(filepath).replace('\x0c\x0c', '')
            except (PDFTextExtractionNotAllowed,
                    PSEOF,
                    PDFEncryptionError,
                    PDFSyntaxError):
                try:
                    return auto_textract(filepath)
                except:
                    return u''
        except NameError:
            LOG.warning('Attempted to use pdfminer but, ' +
                        'pdfminer not installed, install to extract PDF text.')
            return u''


def handle_ebook_files(filepath):
    try:
        # cmd = ['mudraw', '-F', 'text', filepath]
        cmd = ['mudraw', '-t', filepath]
        p = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
        stdout, stderr = p.communicate()
        return stdout
    except OSError:
        LOG.warning('The mudraw command is not installed, ' +
                    "will not be able to extract text from ebook files " +
                    "and pdf's")
        return u''


def handle_pdf_files(filepath, mudraw=True):
    """
    if mudraw is True then 'mudraw' will be used to extract pdf text.
    Else, 'pdfminer' will be used.
    """
    if mudraw:
        txt = handle_ebook_files(filepath)
        if not txt:
            LOG.debug('falling back to pdfminer')
            return handle_pdf_files(filepath, mudraw=False)
    else:
        txt = handle_pdf_files_pdfminer(filepath)
    return txt


def handle_doc_files(filepath):
    try:
        p = Popen(['antiword', filepath], stdout=PIPE, stderr=DEVNULL)
        stdout, stderr = p.communicate()
        return stdout
    except IOError:
        LOG.warning('the antiword program is not installed, ' +
                    "will not be able to extract text from '.doc' files.")
        return u''


def handle_docx_files(filepath):
    try:
        try:
            document = Document(filepath)
            return '\n\n'.join([graph.text for graph in document.paragraphs])
        except IOError:
            LOG.debug('Docx could not extract the files text.')
    except NameError:
        LOG.warning('Attempted to use docx but, ' +
                    "docx not installed, install to extract '.docx' text.")
    return u''


def handle_odt_files(filepath):
    try:
        p = Popen(['odt2txt', filepath], stdout=PIPE, stderr=DEVNULL)
        stdout, stderr = p.communicate()
        return stdout
    except OSError:
        LOG.warning('The odt2txt program is not installed, ' +
                    "will not be able to extract text from '.odt' files.")
        return u''


def handle_rtf_files(filepath):
    try:
        cmd = ['unrtf', filepath]
        p = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
        stdout, stderr = p.communicate()
        try:
            return BeautifulSoup(stdout, 'lxml').text
        except NameError:
            LOG.warning('Attempted to use BeautifulSoup but, ' +
                        'BeautifulSoup (bs4) is not installed,' +
                        'will not be able to parse XML and HTML.')
            return stdout
    except OSError:
        LOG.warning('The unrtf command is not installed,' +
                    "will not be able to extract text from '.rtf' files.")
        return u''


BFILEHANDLEDICT = {u'.doc': handle_doc_files,
                   u'.docx': handle_docx_files,
                   u'.odt': handle_odt_files,
                   u'.pdf': handle_pdf_files,
                   u'.rtf': handle_rtf_files,
                   u'.xps': handle_ebook_files,
                   u'.epub': handle_ebook_files,
                   u'.cbz': handle_ebook_files,
                   }


def document_to_text(filepath, okext=OKEXT):
    ext = get_file_suffixes(filepath).lower()
    if ext in okext:
        try:
            parsefunc = BFILEHANDLEDICT[ext]
            text = parsefunc(filepath)
        except KeyError:
            text = auto_textract(filepath)
        if text:
            return auto_unicode_dang_it(text)
    return u''


def parse_binary_from_file(filename):
    if isfile(filename):
        txt = document_to_text(filename)
        if txt is None:
            return u''
        elif len(re.findall('\\x00', txt)) > 10:
            return u''
        elif not bool(txt.split()):
            return u''
        else:
            return txt
    else:
        raise ValueError('filename did not lead to a file')


def parse_binary_from_string(string, suffix=None, **xargs):
    """
    suffix = extension
    """
    if not suffix:
        LOG.debug('Extension not provided, trying guess based on mime time.')
        suffix = guess_ext_from_mime(string)
    return write_and_op_on_tmp(data=string,
                               function=parse_binary_from_file,
                               suffix=suffix)


def parse_binary(string=None, fname=None, suffix=None, okext=OKEXT,
                 tryagain=True, **xargs):
    """
    Parse a binary file or string.
    """
    stringbool = bool(string)
    if (not stringbool) and bool(fname) and (get_file_suffixes(fname) in okext):
        return parse_binary_from_file(fname)
    elif fname and (not suffix) and stringbool:
        suffix = auto_unicode_dang_it('.' +
                                      fname.split('.')[-1]).encode('ascii')
    elif (not suffix) and stringbool:
        suffix = guess_ext_from_mime(string)
    else:
        if (suffix not in okext) or (fname and
                                     (get_file_suffixes(fname) not in okext)):
            return None
        else:
            raise ValueError('Did not provide string or fname')

    if suffix.lower() not in okext:
        if not fname:
            fname = ''
        return None
    prsd = parse_binary_from_string(string=string, suffix=suffix)
    if tryagain and not (len(prsd) > 0):
        try:
            extbymime = guess_ext_from_mime(string)
        except KeyError:
            extbymime = None
        if extbymime and (extbymime.lower() in okext):
            try:
                return parse_binary_from_string(string,
                                                suffix=extbymime)
            except ValueError:
                LOG.debug('body len=0, and mime ' +
                          'derived ext resulted in ValueError, giving up.\t' +
                          'Supplied ext:\t' + suffix + '\t' +
                          'Mime derived ext:\t' + str(extbymime) + '\t' +
                          'Filename:\t' + str(fname))
        else:
            pass
    else:
        pass
    return prsd
