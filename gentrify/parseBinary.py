# -*- coding: utf-8 -*-
__title__ = 'ellis_island'
__author__ = 'Steven Cutting'
__author_email__ = 'steven.c.projects@gmail.com'
__created_on__ = '6/12/2015'


from subprocess import Popen, PIPE

from docx import Document
# from xlrd import XLRDError
# import pandas
import zipfile

from textract import process
from textract.exceptions import(ExtensionNotSupported,
                                ShellError)
# http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import(PDFTextExtractionNotAllowed,
                                 PSEOF,
                                 PDFEncryptionError,
                                 PDFSyntaxError)
from cStringIO import StringIO
import bs4
from tempfile import NamedTemporaryFile
from pathlib import Path
import re

from magic import from_buffer
# import mimetypes
# mimetypes.init()
# from mimetypes import guess_extension

from gentrify.fixEncoding import auto_unicode_dang_it

import logging
LOG = logging.getLogger(__name__)


OKEXT = set([u'.doc',
             u'.docx',
             u'.pdf',
             u'.txt',
             u'.html',
             u'.htm',
             u'.eml',
             u'.rtf',
             ])

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
        return process(filepath, language='nor')
    except (ExtensionNotSupported,
            IndexError,
            ShellError,
            TypeError):
        return u''


# def pandas_print_full(x):
#     pandas.set_option('display.max_rows', len(x))
#     g = unicode(x)
#     pandas.reset_option('display.max_rows')
#     return g


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    with file(path, 'rb') as fp:
        try:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                          password=password, caching=caching,
                                          check_extractable=True):
                interpreter.process_page(page)
            # fp.close()
            device.close()
            str_ = retstr.getvalue()
            retstr.close()
            return str_
        except(TypeError):
            return u''


def document_to_text(filepath):
    # ----------------------
    # Text doc files
    if filepath.lower().endswith(".doc"):
        cmd = ['antiword', filepath]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    elif filepath.lower().endswith(".docx"):
        document = Document(filepath)
        return '\n\n'.join([graph.text for graph in document.paragraphs])
    # elif filepath.lower().endswith(".odt"):  # Not supporting currently
    #     return None
        # cmd = ['odt2txt', filepath]
        # p = Popen(cmd, stdout=PIPE)
        # stdout, stderr = p.communicate()
        # return stdout.decode('ascii', 'ignore')
    elif filepath.lower().endswith(".rtf"):
        cmd = ['unrtf', filepath]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return bs4.BeautifulSoup(stdout.decode('ascii', 'ignore')).text
    # ----------------------
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
    # ----------------------
    # Other
    elif filepath.lower().endswith(".pdf"):
        try:
            return convert_pdf_to_txt(filepath).replace('\x0c\x0c', '')
        except (PDFTextExtractionNotAllowed,
                PSEOF,
                PDFEncryptionError,
                PDFSyntaxError):
            try:
                auto_textract(filepath)
            except:
                return u''
    # will handle zips another way
    # elif filepath[-4:].lower() == ".zip":
    #    with TempDir() as dastmpdir:
    #        try:
    #            extractedfiles = handle_zip_files(filepath, dastmpdir)
    #            return [document_to_text('{}/{}'.format(dastmpdir,path))
    #                    for path in extractedfiles]
    #        except zipfile.BadZipfile:
    #            return None
    else:
        return auto_textract(filepath)


def extract_text(filename):
    filenameobj = Path(filename)
    if filenameobj.is_file():
        txt = document_to_text(filename)
        if txt is None:
            return u''
        elif len(re.findall('\\x00', txt)) > 10:
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


def parse_binary_from_string(fdata, fname=u'', suffix=u''):
    """
    Must supply fname or suffix (i.e. extension).
    """
    if not suffix:
        suffix = auto_unicode_dang_it('.' +
                                      fname.split('.')[-1]).encode('ascii')
    # extbymime = guess_extension(from_buffer(fdata, mime=True),
    #                             strict=True)
    try:
        extbymime = MIMETYPES[from_buffer(fdata, mime=True)]
    except KeyError:
        return {u'body': u''}

    if extbymime != suffix:
        LOG.error('Guessed ext does not match the provided ext.')

    with NamedTemporaryFile(suffix=extbymime) as tmp:
        tmp.file.write(fdata)
        tmp.file.seek(0)
        # try:
        filedict = parse_binary(tmp.name)
        # except(AttributeError):
        #    atchdict['filedata'] = u''
    filedict['rawbody'] = fdata
    return filedict
