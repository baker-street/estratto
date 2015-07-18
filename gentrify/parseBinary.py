# -*- coding: utf-8 -*-
__title__ = 'gentrify'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'

import logging
LOG = logging.getLogger(__name__)

from os.path import dirname
import zipfile
from subprocess import Popen, PIPE
import re
from cStringIO import StringIO
from magic import from_buffer


from pathlib import Path
# from xlrd import XLRDError
import pandas
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


from gentrify.fixEncoding import auto_unicode_dang_it
from gentrify import utils
from gentrify.utils import write_and_op_on_tmp

CONFFILE = dirname(utils.__file__) + '/defconf.json'
OKEXT = set(utils.load_json(CONFFILE)['ok_ext_set'])

MIMETYPES = {'application/pdf': '.pdf',
             'application/msword': '.doc',
             'application/vnd.\
             openxmlformats-officedocument.wordprocessingml.document': '.docx',
             'text/plain': '.txt',
             'message/rfc822': '.eml',
             'text/html': '.html',
             'application/rtf': '.rtf',
             }


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
            log = 'textract not installed, install for robust text extraction.'
            LOG.warning('Attempted to use textract but, ' + log)
            return u''
    except (ExtensionNotSupported,
            IndexError,
            ShellError,
            TypeError):
        return u''


def pandas_print_full(x):
    pandas.set_option('display.max_rows', len(x))
    g = unicode(x)
    pandas.reset_option('display.max_rows')
    return g


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


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()
    with StringIOContext() as retstr:
        with TextConverterContext(rsrcmgr,
                                  retstr,
                                  codec=codec,
                                  laparams=laparams) as device:
            with file(path, 'rb') as fp:
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
                        interpreter.process_page(page)
                    str_ = retstr.getvalue()
                    if str_:
                        return str_
                    else:
                        return u''
                except(TypeError):
                    return u''


def handle_pdf_files(filepath):
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


def handle_doc_files(filepath):
    try:
        cmd = ['antiword', filepath]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout
    except OSError:
        LOG.warning('The antiword command is not installed, ' +
                    "will not be able to extract text from '.doc' files.")
        return u''


def handle_docx_files(filepath):
    try:
        document = Document(filepath)
        return '\n\n'.join([graph.text for graph in document.paragraphs])
    except NameError:
        LOG.warning('Attempted to use textract but, ' +
                    "docx not installed, install to extract '.docx' text.")
        return u''


def handle_rtf_files(filepath):
    try:
        cmd = ['unrtf', filepath]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        try:
            return BeautifulSoup(stdout).text
        except NameError:
            LOG.warning('Attempted to use BeautifulSoup but, ' +
                        'BeautifulSoup (bs4) is not installed,' +
                        'will not be able to parse XML and HTML.')
            return stdout
    except OSError:
        LOG.warning('The unrtf command is not installed,' +
                    "will not be able to extract text from '.rtf' files.")
        return u''


def handle_odt_files(filepath):
    return u''
    # try:
    #     # cmd = ['odt2txt', filepath]
    #     # p = Popen(cmd, stdout=PIPE)
    #     # stdout, stderr = p.communicate()
    #     # return stdout.decode('ascii', 'ignore')
    # except OSError:
    #     LOG.warning('The odt2txt command is not installed,' +
    #                 "will not be able to extract text from '.odt' files.")
    #     return u''


BFILEHANDLEDICT = {u'.doc': handle_doc_files,
                   u'.docx': handle_docx_files,
                   u'.pdf': handle_pdf_files,
                   u'.rtf': handle_rtf_files,
                   }


def document_to_text(filepath, okext=OKEXT):
    ext = ''.join(Path(filepath).suffixes).lower()
    if ext in okext:
        try:
            parsefunc = BFILEHANDLEDICT[ext]
            text = parsefunc(filepath)
        except KeyError:
            text = auto_textract(filepath)
        if text:
            return auto_unicode_dang_it(text)
    return u''


def _OLD_document_to_text(filepath):
    ext = ''.join(Path(filepath).suffixes).lower()
    # ----------------------
    # Text doc files
    if ext == ".doc":
        return handle_doc_files(filepath)
    elif ext == ".docx":
        return handle_docx_files(filepath)
    elif ext == ".odt":  # Not supporting currently
        return handle_odt_files(filepath)
    elif ext == ".rtf":
        return handle_rtf_files(filepath)
    # ----------------------
    # Other
    elif ext == ".pdf":
        return handle_pdf_files(filepath)
    else:
        return auto_textract(filepath)
    # will handle zips another way
    # elif filepath[-4:].lower() == ".zip":
    #    with TempDir() as dastmpdir:
    #        try:
    #            extractedfiles = handle_zip_files(filepath, dastmpdir)
    #            return [document_to_text('{}/{}'.format(dastmpdir,path))
    #                    for path in extractedfiles]
    #        except zipfile.BadZipfile:
    #            return None
    # ----------------------  # Might add back in later
    # SpreadSheets
    # elif filepath.lower().endswith((".xls", ".xlsx")):
        # Not supporting currently
        # return None
        # try:
        #     return auto_textract(filepath)
        # except (XLRDError,
        #        IndexError,
        #        AssertionError,
        #        OverflowError):
        #    return None
        # try:
        #    # cmd = ['x_x', filepath]
        #    # p = Popen(cmd, stdout=PIPE)
        #    # stdout, stderr = p.communicate()
        #    # return stdout.decode('ascii', 'ignore')
        #     return pandas_print_full(pandas.read_excel(filepath))
        # except (XLRDError,IndexError,AssertionError,OverflowError):
        #     return None


def extract_text(filename):
    filenameobj = Path(filename)
    if filenameobj.is_file():
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


def parse_binary(fname, extset=OKEXT):
    if not fname.lower().endswith(tuple(extset)):
        return {u'body': u''}
    else:
        return {u'body': auto_unicode_dang_it(extract_text(fname)),
                }

EXTWARN = """Guessed ext does not match the provided ext.\tguess:{gext}\
\text:{ext}\tfname:{fname}"""


def parse_binary_from_string(fdata, fname=u'', suffix=u''):
    """
    Must supply fname or suffix (i.e. extension).
    """
    if not suffix:
        suffix = auto_unicode_dang_it('.' +
                                      fname.split('.')[-1]).encode('ascii')
    try:
        extbymime = MIMETYPES[from_buffer(fdata, mime=True)]
    except KeyError:
        return {u'body': u''}

    if extbymime.lower() != suffix.lower():
        LOG.debug(EXTWARN.format(gext=extbymime, ext=suffix, fname=fname))
    filedict = write_and_op_on_tmp(data=fdata,
                                   function=parse_binary,
                                   suffix=extbymime)
    filedict['rawbody'] = fdata
    return filedict
