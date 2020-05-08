# -*- coding: utf-8 -*-
#
# vim: sw=4:expandtab:foldmethod=marker
#
# Copyright (c) 2006, Mathieu Fenniak
# Copyright (c) 2007, Ashish Kulkarni <kulkarni.ashish@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
A pure-Python PDF library with an increasing number of capabilities.
See README for links to FAQ, documentation, homepage, etc.
"""

__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

import sys
from hashlib import md5
from io import BytesIO

from .document_information import DocumentInformation
from .generic import *
from .page_object import PageObject
from .utils import _alg33_1, convertToInt, _alg34, _alg35
from .utils import isString, b_, formatWarning
from .utils import readNonWhitespace, readUntilWhitespace, ConvertFunctionsToVirtualList


class PdfFileReader(object):
    """
    Initializes a PdfFileReader object.  This operation can take some time, as
    the PDF stream's cross-reference tables are read into memory.

    :param stream: A File object or an object that supports the standard read
        and seek methods similar to a File object. Could also be a
        string representing a path to a PDF file.
    :param bool strict: Determines whether user should be warned of all
        problems and also causes some correctable problems to be fatal.
        Defaults to ``True``.
    :param warndest: Destination for logging warnings (defaults to
        ``sys.stderr``).
    :param bool overwriteWarnings: Determines whether to override Python's
        ``warnings.py`` module with a custom implementation (defaults to
        ``True``).
    """

    def __init__(self, stream, strict=True, warndest=None, overwriteWarnings=True):
        if overwriteWarnings:
            # have to dynamically override the default showwarning since there are no
            # public methods that specify the 'file' parameter
            def _showwarning(message, category, filename, lineno, file=warndest, line=None):
                if file is None:
                    file = sys.stderr
                try:
                    file.write(formatWarning(message, category, filename, lineno, line))
                except IOError:
                    pass

            warnings.showwarning = _showwarning
        self.trailer = None
        self.strict = strict
        self.flattenedPages = None
        self.resolvedObjects = {}
        self.xrefIndex = 0
        self._pageId2Num = None  # map page IndirectRef number to Page Number
        self._override_encryption = False
        # self.stream = stream
        if isString(stream):
            with open(stream, "rb") as f:
                self.stream = BytesIO(b_(f.read()))
        else:
            self.stream = BytesIO(stream)
        self.read(self.stream)
        # try:
        #     self.stream = BytesIO(stream)
        #     self.read(stream)
        # except (UnicodeDecodeError, AttributeError):
        #     if hasattr(stream, 'mode') and 'b' not in stream.mode:
        #         warnings.warn("PdfFileReader stream/file object is not in binary mode. It may not be read correctly.",
        #                       utils.PdfReadWarning)
        #     if isString(stream):
        #         fileobj = open(stream, 'rb')
        #         stream = BytesIO(b_(fileobj.read()))
        #         fileobj.close()
        #     self.read(stream)
        #     self.stream = stream


    def getDocumentInfo(self):
        """
        Retrieves the PDF file's document information dictionary, if it exists.
        Note that some PDF files use metadata streams instead of docinfo
        dictionaries, and these metadata streams will not be accessed by this
        function.

        :return: the document information of this PDF file
        :rtype: :class:`DocumentInformation<pdf.DocumentInformation>` or ``None`` if none exists.
        """
        if "/Info" not in self.trailer:
            return None
        obj = self.trailer['/Info']
        retval = DocumentInformation()
        retval.update(obj)
        return retval

    documentInfo = property(lambda self: self.getDocumentInfo(), None, None)
    """Read-only property that accesses the :meth:`getDocumentInfo()<PdfFileReader.getDocumentInfo>` function."""

    def getXmpMetadata(self):
        """
        Retrieves XMP (Extensible Metadata Platform) data from the PDF document
        root.

        :return: a :class:`XmpInformation<xmp.XmpInformation>`
            instance that can be used to access XMP metadata from the document.
        :rtype: :class:`XmpInformation<xmp.XmpInformation>` or
            ``None`` if no metadata was found on the document root.
        """
        try:
            self._override_encryption = True
            return self.trailer["/Root"].getXmpMetadata()
        finally:
            self._override_encryption = False

    xmpMetadata = property(lambda self: self.getXmpMetadata(), None, None)
    """
    Read-only property that accesses the
    :meth:`getXmpMetadata()<PdfFileReader.getXmpMetadata>` function.
    """

    def getNumPages(self):
        """
        Calculates the number of pages in this PDF file.

        :return: number of pages
        :rtype: int
        :raises PdfReadError: if file is encrypted and restrictions prevent
            this action.
        """

        # Flattened pages will not work on an Encrypted PDF;
        # the PDF file's page count is used in this case. Otherwise,
        # the original method (flattened page count) is used.
        if self.isEncrypted:
            try:
                self._override_encryption = True
                self.decrypt('')
                return self.trailer["/Root"]["/Pages"]["/Count"]
            except:
                raise utils.PdfReadError("File has not been decrypted")
            finally:
                self._override_encryption = False
        else:
            if self.flattenedPages is None:
                self._flatten()
            return len(self.flattenedPages)

    numPages = property(lambda self: self.getNumPages(), None, None)
    """
    Read-only property that accesses the
    :meth:`getNumPages()<PdfFileReader.getNumPages>` function.
    """

    def getPage(self, pageNumber):
        """
        Retrieves a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: a :class:`PageObject<pdf.PageObject>` instance.
        :rtype: :class:`PageObject<pdf.PageObject>`
        """
        ## ensure that we're not trying to access an encrypted PDF
        # assert not self.trailer.has_key("/Encrypt")
        if self.flattenedPages is None:
            self._flatten()
        return self.flattenedPages[pageNumber]

    namedDestinations = property(lambda self:
                                 self.getNamedDestinations(), None, None)
    """
    Read-only property that accesses the
    :meth:`getNamedDestinations()<PdfFileReader.getNamedDestinations>` function.
    """

    # A select group of relevant field attributes. For the complete list,
    # see section 8.6.2 of the PDF 1.7 reference.

    def getFields(self, tree=None, retval=None, fileobj=None):
        """
        Extracts field data if this PDF contains interactive form fields.
        The *tree* and *retval* parameters are for recursive use.

        :param tree:
        :param retval:
        :param fileobj: A file object (usually a text file) to write
            a report to on all interactive form fields found.
        :return: A dictionary where each key is a field name, and each
            value is a :class:`Field<PyPDF2.generic.Field>` object. By
            default, the mapping name is used for keys.
        :rtype: dict, or ``None`` if form data could not be located.
        """
        fieldAttributes = {"/FT": "Field Type", "/Parent": "Parent",
                           "/T": "Field Name", "/TU": "Alternate Field Name",
                           "/TM": "Mapping Name", "/Ff": "Field Flags",
                           "/V": "Value", "/DV": "Default Value"}
        if retval is None:
            retval = {}
            catalog = self.trailer["/Root"]
            # get the AcroForm tree
            if "/AcroForm" in catalog:
                tree = catalog["/AcroForm"]
            else:
                return None
        if tree is None:
            return retval

        self._checkKids(tree, retval, fileobj)
        for attr in fieldAttributes:
            if attr in tree:
                # Tree is a field
                self._buildField(tree, retval, fileobj, fieldAttributes)
                break

        if "/Fields" in tree:
            fields = tree["/Fields"]
            for f in fields:
                field = f.getObject()
                self._buildField(field, retval, fileobj, fieldAttributes)

        return retval

    def _buildField(self, field, retval, fileobj, fieldAttributes):
        self._checkKids(field, retval, fileobj)
        try:
            key = field["/TM"]
        except KeyError:
            try:
                key = field["/T"]
            except KeyError:
                # Ignore no-name field for now
                return
        if fileobj:
            self._writeField(fileobj, field, fieldAttributes)
            fileobj.write("\n")
        retval[key] = Field(field)

    def _checkKids(self, tree, retval, fileobj):
        if "/Kids" in tree:
            # recurse down the tree
            for kid in tree["/Kids"]:
                self.getFields(kid.getObject(), retval, fileobj)

    def _writeField(self, fileobj, field, fieldAttributes):
        order = ["/TM", "/T", "/FT", "/Parent", "/TU", "/Ff", "/V", "/DV"]
        for attr in order:
            attrName = fieldAttributes[attr]
            try:
                if attr == "/FT":
                    # Make the field type value more clear
                    types = {"/Btn": "Button", "/Tx": "Text", "/Ch": "Choice",
                             "/Sig": "Signature"}
                    if field[attr] in types:
                        fileobj.write(attrName + ": " + types[field[attr]] + "\n")
                elif attr == "/Parent":
                    # Let's just write the name of the parent
                    try:
                        name = field["/Parent"]["/TM"]
                    except KeyError:
                        name = field["/Parent"]["/T"]
                    fileobj.write(attrName + ": " + name + "\n")
                else:
                    fileobj.write(attrName + ": " + str(field[attr]) + "\n")
            except KeyError:
                # Field attribute is N/A or unknown, so don't write anything
                pass

    def getFormTextFields(self):
        """ Retrieves form fields from the document with textual data (inputs, dropdowns)
        """
        # Retrieve document form fields
        formfields = self.getFields()
        return dict(
            (formfields[field]['/T'], formfields[field].get('/V')) for field in formfields \
            if formfields[field].get('/FT') == '/Tx'
        )

    def getNamedDestinations(self, tree=None, retval=None):
        """
        Retrieves the named destinations present in the document.

        :return: a dictionary which maps names to
            :class:`Destinations<PyPDF2.generic.Destination>`.
        :rtype: dict
        """
        if retval is None:
            retval = {}
            catalog = self.trailer["/Root"]

            # get the name tree
            if "/Dests" in catalog:
                tree = catalog["/Dests"]
            elif "/Names" in catalog:
                names = catalog['/Names']
                if "/Dests" in names:
                    tree = names['/Dests']

        if tree is None:
            return retval

        if "/Kids" in tree:
            # recurse down the tree
            for kid in tree["/Kids"]:
                self.getNamedDestinations(kid.getObject(), retval)

        if "/Names" in tree:
            names = tree["/Names"]
            for i in range(0, len(names), 2):
                key = names[i].getObject()
                val = names[i + 1].getObject()
                if isinstance(val, DictionaryObject) and '/D' in val:
                    val = val['/D']
                dest = self._buildDestination(key, val)
                if dest is not None:
                    retval[key] = dest

        return retval

    outlines = property(lambda self: self.getOutlines(), None, None)
    """
    Read-only property that accesses the
        :meth:`getOutlines()<PdfFileReader.getOutlines>` function.
    """

    def getOutlines(self, node=None, outlines=None):
        """
        Retrieves the document outline present in the document.

        :return: a nested list of :class:`Destinations<PyPDF2.generic.Destination>`.
        """
        if outlines is None:
            outlines = []
            catalog = self.trailer["/Root"]

            # get the outline dictionary and named destinations
            if "/Outlines" in catalog:
                try:
                    lines = catalog["/Outlines"]
                except utils.PdfReadError:
                    # this occurs if the /Outlines object reference is incorrect
                    # for an example of such a file, see https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf
                    # so continue to load the file without the Bookmarks
                    return outlines

                if "/First" in lines:
                    node = lines["/First"]
            self._namedDests = self.getNamedDestinations()

        if node is None:
            return outlines

        # see if there are any more outlines
        while True:
            outline = self._buildOutline(node)
            if outline:
                outlines.append(outline)

            # check for sub-outlines
            if "/First" in node:
                subOutlines = []
                self.getOutlines(node["/First"], subOutlines)
                if subOutlines:
                    outlines.append(subOutlines)

            if "/Next" not in node:
                break
            node = node["/Next"]

        return outlines

    def _getPageNumberByIndirect(self, indirectRef):
        """Generate _pageId2Num"""
        if self._pageId2Num is None:
            id2num = {}
            for i, x in enumerate(self.pages):
                id2num[x.indirectRef.idnum] = i
            self._pageId2Num = id2num

        if isinstance(indirectRef, int):
            idnum = indirectRef
        else:
            idnum = indirectRef.idnum

        ret = self._pageId2Num.get(idnum, -1)
        return ret

    def getPageNumber(self, page):
        """
        Retrieve page number of a given PageObject

        :param PageObject page: The page to get page number. Should be
            an instance of :class:`PageObject<PyPDF2.pdf.PageObject>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        indirectRef = page.indirectRef
        ret = self._getPageNumberByIndirect(indirectRef)
        return ret

    def getDestinationPageNumber(self, destination):
        """
        Retrieve page number of a given Destination object

        :param Destination destination: The destination to get page number.
             Should be an instance of
             :class:`Destination<PyPDF2.pdf.Destination>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        indirectRef = destination.page
        ret = self._getPageNumberByIndirect(indirectRef)
        return ret

    def _buildDestination(self, title, array):
        page, typ = array[0:2]
        array = array[2:]
        return Destination(title, page, typ, *array)

    def _buildOutline(self, node):
        dest, title, outline = None, None, None

        if "/A" in node and "/Title" in node:
            # Action, section 8.5 (only type GoTo supported)
            title = node["/Title"]
            action = node["/A"]
            if action["/S"] == "/GoTo":
                dest = action["/D"]
        elif "/Dest" in node and "/Title" in node:
            # Destination, section 8.2.1
            title = node["/Title"]
            dest = node["/Dest"]

        # if destination found, then create outline
        if dest:
            if isinstance(dest, ArrayObject):
                outline = self._buildDestination(title, dest)
            elif isString(dest) and dest in self._namedDests:
                outline = self._namedDests[dest]
                outline[NameObject("/Title")] = title
            else:
                raise utils.PdfReadError("Unexpected destination %r" % dest)
        return outline

    pages = property(lambda self: ConvertFunctionsToVirtualList(self.getNumPages, self.getPage),
                     None, None)
    """
    Read-only property that emulates a list based upon the
    :meth:`getNumPages()<PdfFileReader.getNumPages>` and
    :meth:`getPage()<PdfFileReader.getPage>` methods.
    """

    def getPageLayout(self):
        """
        Get the page layout.
        See :meth:`setPageLayout()<PdfFileWriter.setPageLayout>`
        for a description of valid layouts.

        :return: Page layout currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self.trailer['/Root']['/PageLayout']
        except KeyError:
            return None

    pageLayout = property(getPageLayout)
    """Read-only property accessing the
    :meth:`getPageLayout()<PdfFileReader.getPageLayout>` method."""

    def getPageMode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfFileWriter.setPageMode>`
        for a description of valid modes.

        :return: Page mode currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self.trailer['/Root']['/PageMode']
        except KeyError:
            return None

    pageMode = property(getPageMode)
    """Read-only property accessing the
    :meth:`getPageMode()<PdfFileReader.getPageMode>` method."""

    def _flatten(self, pages=None, inherit=None, indirectRef=None):
        inheritablePageAttributes = (
            NameObject("/Resources"), NameObject("/MediaBox"),
            NameObject("/CropBox"), NameObject("/Rotate")
        )
        if inherit is None:
            inherit = dict()
        if pages is None:
            self.flattenedPages = []
            catalog = self.trailer["/Root"].getObject()
            pages = catalog["/Pages"].getObject()

        t = "/Pages"
        if "/Type" in pages:
            t = pages["/Type"]

        if t == "/Pages":
            for attr in inheritablePageAttributes:
                if attr in pages:
                    inherit[attr] = pages[attr]
            for page in pages["/Kids"]:
                addt = {}
                if isinstance(page, IndirectObject):
                    addt["indirectRef"] = page
                self._flatten(page.getObject(), inherit, **addt)
        elif t == "/Page":
            for attr, value in list(inherit.items()):
                # if the page has it's own value, it does not inherit the
                # parent's value:
                if attr not in pages:
                    pages[attr] = value
            pageObj = PageObject(self, indirectRef)
            pageObj.update(pages)
            self.flattenedPages.append(pageObj)

    def _getObjectFromStream(self, indirectReference):
        # indirect reference to object in object stream
        # read the entire object stream into memory
        debug = False
        stmnum, idx = self.xref_objStm[indirectReference.idnum]
        if debug: print(("Here1: %s %s" % (stmnum, idx)))
        objStm = IndirectObject(stmnum, 0, self).getObject()
        if debug: print(("Here2: objStm=%s.. stmnum=%s data=%s" % (objStm, stmnum, objStm.getData())))
        # This is an xref to a stream, so its type better be a stream
        assert objStm['/Type'] == '/ObjStm'
        # /N is the number of indirect objects in the stream
        assert idx < objStm['/N']
        streamData = BytesIO(b_(objStm.getData()))
        for i in range(objStm['/N']):
            readNonWhitespace(streamData)
            streamData.seek(-1, 1)
            objnum = NumberObject.readFromStream(streamData)
            readNonWhitespace(streamData)
            streamData.seek(-1, 1)
            offset = NumberObject.readFromStream(streamData)
            readNonWhitespace(streamData)
            streamData.seek(-1, 1)
            if objnum != indirectReference.idnum:
                # We're only interested in one object
                continue
            if self.strict and idx != i:
                raise utils.PdfReadError("Object is in wrong index.")
            streamData.seek(objStm['/First'] + offset, 0)
            if debug:
                pos = streamData.tell()
                streamData.seek(0, 0)
                lines = streamData.readlines()
                for j in range(0, len(lines)):
                    print((lines[j]))
                streamData.seek(pos, 0)
            # noinspection PyUnusedLocal
            try:
                obj = readObject(streamData, self)
            except utils.PdfStreamError as e:
                # Stream object cannot be read. Normally, a critical error, but
                # Adobe Reader doesn't complain, so continue (in strict mode?)
                e = sys.exc_info()[1]
                warnings.warn("Invalid stream (index %d) within object %d %d: %s" % \
                              (i, indirectReference.idnum, indirectReference.generation, e), utils.PdfReadWarning)

                if self.strict:
                    raise utils.PdfReadError("Can't read object stream: %s" % e)
                # Replace with null. Hopefully it's nothing important.
                obj = NullObject()
            return obj

        if self.strict: raise utils.PdfReadError("This is a fatal error in strict mode.")
        return NullObject()

    def getObject(self, indirectReference):
        debug = False
        if debug: print(("looking at:", indirectReference.idnum, indirectReference.generation))
        retval = self.cacheGetIndirectObject(indirectReference.generation,
                                             indirectReference.idnum)
        if retval is not None:
            return retval
        if indirectReference.generation == 0 and \
                indirectReference.idnum in self.xref_objStm:
            retval = self._getObjectFromStream(indirectReference)
        elif indirectReference.generation in self.xref and \
                indirectReference.idnum in self.xref[indirectReference.generation]:
            start = self.xref[indirectReference.generation][indirectReference.idnum]
            if debug: print(
                ("  Uncompressed Object", indirectReference.idnum, indirectReference.generation, ":", start))
            self.stream.seek(start, 0)
            idnum, generation = self.readObjectHeader(self.stream)
            if idnum != indirectReference.idnum and self.xrefIndex:
                # Xref table probably had bad indexes due to not being zero-indexed
                if self.strict:
                    raise utils.PdfReadError(
                        "Expected object ID (%d %d) does not match actual (%d %d); xref table not zero-indexed." \
                        % (indirectReference.idnum, indirectReference.generation, idnum, generation))
                else:
                    pass  # xref table is corrected in non-strict mode
            elif idnum != indirectReference.idnum and self.strict:
                # some other problem
                raise utils.PdfReadError("Expected object ID (%d %d) does not match actual (%d %d)." \
                                         % (indirectReference.idnum, indirectReference.generation, idnum, generation))
            if self.strict:
                assert generation == indirectReference.generation
            retval = readObject(self.stream, self)

            # override encryption is used for the /Encrypt dictionary
            if not self._override_encryption and self.isEncrypted:
                # if we don't have the encryption key:
                if not hasattr(self, '_decryption_key'):
                    raise utils.PdfReadError("file has not been decrypted")
                # otherwise, decrypt here...
                import struct
                pack1 = struct.pack("<i", indirectReference.idnum)[:3]
                pack2 = struct.pack("<i", indirectReference.generation)[:2]
                key = self._decryption_key + pack1 + pack2
                assert len(key) == (len(self._decryption_key) + 5)
                md5_hash = md5(key).digest()
                key = md5_hash[:min(16, len(self._decryption_key) + 5)]
                retval = self._decryptObject(retval, key)
        else:
            warnings.warn("Object %d %d not defined." % (indirectReference.idnum,
                                                         indirectReference.generation), utils.PdfReadWarning)
            # if self.strict:
            raise utils.PdfReadError("Could not find object.")
        self.cacheIndirectObject(indirectReference.generation,
                                 indirectReference.idnum, retval)
        return retval

    def _decryptObject(self, obj, key):
        if isinstance(obj, ByteStringObject) or isinstance(obj, TextStringObject):
            obj = createStringObject(utils.RC4_encrypt(key, obj.original_bytes))
        elif isinstance(obj, StreamObject):
            obj._data = utils.RC4_encrypt(key, obj._data)
        elif isinstance(obj, DictionaryObject):
            for dictkey, value in list(obj.items()):
                obj[dictkey] = self._decryptObject(value, key)
        elif isinstance(obj, ArrayObject):
            for i in range(len(obj)):
                obj[i] = self._decryptObject(obj[i], key)
        return obj

    def readObjectHeader(self, stream):
        # Should never be necessary to read out whitespace, since the
        # cross-reference table should put us in the right spot to read the
        # object header.  In reality... some files have stupid cross reference
        # tables that are off by whitespace bytes.
        extra = False
        utils.skipOverComment(stream)
        extra |= utils.skipOverWhitespace(stream)
        stream.seek(-1, 1)
        idnum = readUntilWhitespace(stream)
        extra |= utils.skipOverWhitespace(stream)
        stream.seek(-1, 1)
        generation = readUntilWhitespace(stream)
        # noinspection PyUnusedLocal
        obj = stream.read(3)
        readNonWhitespace(stream)
        stream.seek(-1, 1)
        if extra and self.strict:
            # not a fatal error
            warnings.warn("Superfluous whitespace found in object header %s %s" % \
                          (idnum, generation), utils.PdfReadWarning)
        return int(idnum), int(generation)

    def cacheGetIndirectObject(self, generation, idnum):
        debug = False
        out = self.resolvedObjects.get((generation, idnum))
        if debug and out:
            print(("cache hit: %d %d" % (idnum, generation)))
        elif debug:
            print(("cache miss: %d %d" % (idnum, generation)))
        return out

    def cacheIndirectObject(self, generation, idnum, obj):
        # return None # Sometimes we want to turn off cache for debugging.
        if (generation, idnum) in self.resolvedObjects:
            msg = "Overwriting cache for %s %s" % (generation, idnum)
            if self.strict:
                raise utils.PdfReadError(msg)
            else:
                warnings.warn(msg)
        self.resolvedObjects[(generation, idnum)] = obj
        return obj

    def read(self, stream):
        debug = False
        if debug: print(">>read", stream)
        # start at the end:
        stream.seek(-1, 2)
        if not stream.tell():
            raise utils.PdfReadError('Cannot read an empty file')
        last1K = stream.tell() - 1024 + 1  # offset of last 1024 bytes of stream
        line = b_('')
        while line[:5] != b_("%%EOF"):
            if stream.tell() < last1K:
                raise utils.PdfReadError("EOF marker not found")
            line = self.readNextEndLine(stream)
            if debug: print("  line:", line)

        # find startxref entry - the location of the xref table
        line = self.readNextEndLine(stream)
        try:
            startxref = int(line)
        except ValueError:
            # 'startxref' may be on the same line as the location
            if not line.startswith(b_("startxref")):
                raise utils.PdfReadError("startxref not found")
            startxref = int(line[9:].strip())
            warnings.warn("startxref on same line as offset")
        else:
            line = self.readNextEndLine(stream)
            if line[:9] != b_("startxref"):
                raise utils.PdfReadError("startxref not found")

        # read all cross reference tables and their trailers
        self.xref = {}
        self.xref_objStm = {}
        self.trailer = DictionaryObject()
        while True:
            # load the xref table
            stream.seek(startxref, 0)
            x = stream.read(1)
            if x == b_("x"):
                # standard cross-reference table
                ref = stream.read(4)
                if ref[:3] != b_("ref"):
                    raise utils.PdfReadError("xref table read error")
                readNonWhitespace(stream)
                stream.seek(-1, 1)
                firsttime = True  # check if the first time looking at the xref table
                while True:
                    num = readObject(stream, self)
                    if firsttime and num != 0:
                        self.xrefIndex = num
                        if self.strict:
                            warnings.warn("Xref table not zero-indexed. ID numbers for objects will be corrected.",
                                          utils.PdfReadWarning)
                            # if table not zero indexed, could be due to error from when PDF was created
                            # which will lead to mismatched indices later on, only warned and corrected if self.strict=True
                    firsttime = False
                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    size = readObject(stream, self)
                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    cnt = 0
                    while cnt < size:
                        line = stream.read(20)

                        # It's very clear in section 3.4.3 of the PDF spec
                        # that all cross-reference table lines are a fixed
                        # 20 bytes (as of PDF 1.7). However, some files have
                        # 21-byte entries (or more) due to the use of \r\n
                        # (CRLF) EOL's. Detect that case, and adjust the line
                        # until it does not begin with a \r (CR) or \n (LF).
                        while line[0] in b_("\x0D\x0A"):
                            stream.seek(-20 + 1, 1)
                            line = stream.read(20)

                        # On the other hand, some malformed PDF files
                        # use a single character EOL without a preceeding
                        # space.  Detect that case, and seek the stream
                        # back one character.  (0-9 means we've bled into
                        # the next xref entry, t means we've bled into the
                        # text "trailer"):
                        if line[-1] in b_("0123456789t"):
                            stream.seek(-1, 1)

                        offset, generation = line[:16].split(b_(" "))
                        offset, generation = int(offset), int(generation)
                        if generation not in self.xref:
                            self.xref[generation] = {}
                        if num in self.xref[generation]:
                            # It really seems like we should allow the last
                            # xref table in the file to override previous
                            # ones. Since we read the file backwards, assume
                            # any existing key is already set correctly.
                            pass
                        else:
                            self.xref[generation][num] = offset
                        cnt += 1
                        num += 1
                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    trailertag = stream.read(7)
                    if trailertag != b_("trailer"):
                        # more xrefs!
                        stream.seek(-7, 1)
                    else:
                        break
                readNonWhitespace(stream)
                stream.seek(-1, 1)
                newTrailer = readObject(stream, self)
                for key, value in list(newTrailer.items()):
                    if key not in self.trailer:
                        self.trailer[key] = value
                if "/Prev" in newTrailer:
                    startxref = newTrailer["/Prev"]
                else:
                    break
            elif x.isdigit():
                # PDF 1.5+ Cross-Reference Stream
                stream.seek(-1, 1)
                idnum, generation = self.readObjectHeader(stream)
                xrefstream = readObject(stream, self)
                assert xrefstream["/Type"] == "/XRef"
                self.cacheIndirectObject(generation, idnum, xrefstream)
                streamData = BytesIO(b_(xrefstream.getData()))
                # Index pairs specify the subsections in the dictionary. If
                # none create one subsection that spans everything.
                idx_pairs = xrefstream.get("/Index", [0, xrefstream.get("/Size")])
                if debug: print(("read idx_pairs=%s" % list(self._pairs(idx_pairs))))
                entrySizes = xrefstream.get("/W")
                assert len(entrySizes) >= 3
                if self.strict and len(entrySizes) > 3:
                    raise utils.PdfReadError("Too many entry sizes: %s" % entrySizes)

                def getEntry(i):
                    # Reads the correct number of bytes for each entry. See the
                    # discussion of the W parameter in PDF spec table 17.
                    if entrySizes[i] > 0:
                        d = streamData.read(entrySizes[i])
                        return convertToInt(d, entrySizes[i])

                    # PDF Spec Table 17: A value of zero for an element in the
                    # W array indicates...the default value shall be used
                    if i == 0:
                        return 1  # First value defaults to 1
                    else:
                        return 0

                def used_before(num, generation):
                    # We move backwards through the xrefs, don't replace any.
                    return num in self.xref.get(generation, []) or \
                           num in self.xref_objStm

                # Iterate through each subsection
                last_end = 0
                for start, size in self._pairs(idx_pairs):
                    # The subsections must increase
                    assert start >= last_end
                    last_end = start + size
                    for num in range(start, start + size):
                        # The first entry is the type
                        xref_type = getEntry(0)
                        # The rest of the elements depend on the xref_type
                        if xref_type == 0:
                            # linked list of free objects
                            # noinspection PyUnusedLocal
                            next_free_object = getEntry(1)
                            # noinspection PyUnusedLocal
                            next_generation = getEntry(2)
                        elif xref_type == 1:
                            # objects that are in use but are not compressed
                            byte_offset = getEntry(1)
                            generation = getEntry(2)
                            if generation not in self.xref:
                                self.xref[generation] = {}
                            if not used_before(num, generation):
                                self.xref[generation][num] = byte_offset
                                if debug: print(("XREF Uncompressed: %s %s" % (
                                    num, generation)))
                        elif xref_type == 2:
                            # compressed objects
                            objstr_num = getEntry(1)
                            obstr_idx = getEntry(2)
                            generation = 0  # PDF spec table 18, generation is 0
                            if not used_before(num, generation):
                                if debug: print(("XREF Compressed: %s %s %s" % (
                                    num, objstr_num, obstr_idx)))
                                self.xref_objStm[num] = (objstr_num, obstr_idx)
                        elif self.strict:
                            raise utils.PdfReadError("Unknown xref type: %s" %
                                                     xref_type)

                trailerKeys = "/Root", "/Encrypt", "/Info", "/ID"
                for key in trailerKeys:
                    if key in xrefstream and key not in self.trailer:
                        self.trailer[NameObject(key)] = xrefstream.raw_get(key)
                if "/Prev" in xrefstream:
                    startxref = xrefstream["/Prev"]
                else:
                    break
            else:
                # bad xref character at startxref.  Let's see if we can find
                # the xref table nearby, as we've observed this error with an
                # off-by-one before.
                stream.seek(-11, 1)
                tmp = stream.read(20)
                xref_loc = tmp.find(b_("xref"))
                if xref_loc != -1:
                    startxref -= (10 - xref_loc)
                    continue
                # No explicit xref table, try finding a cross-reference stream.
                stream.seek(startxref, 0)
                found = False
                for look in range(5):
                    if stream.read(1).isdigit():
                        # This is not a standard PDF, consider adding a warning
                        startxref += look
                        found = True
                        break
                if found:
                    continue
                # no xref table found at specified location
                raise utils.PdfReadError("Could not find xref table at specified location")
        # if not zero-indexed, verify that the table is correct; change it if necessary
        if self.xrefIndex and not self.strict:
            loc = stream.tell()
            for gen in self.xref:
                if gen == 65535: continue
                for id in self.xref[gen]:
                    stream.seek(self.xref[gen][id], 0)
                    try:
                        pid, pgen = self.readObjectHeader(stream)
                    except ValueError:
                        break
                    if pid == id - self.xrefIndex:
                        self._zeroXref(gen)
                        break
                    # if not, then either it's just plain wrong, or the non-zero-index is actually correct
            stream.seek(loc, 0)  # return to where it was

    def _zeroXref(self, generation):
        self.xref[generation] = dict((k - self.xrefIndex, v) for (k, v) in list(self.xref[generation].items()))

    def _pairs(self, array):
        i = 0
        while True:
            yield array[i], array[i + 1]
            i += 2
            if (i + 1) >= len(array):
                break

    def readNextEndLine(self, stream):
        debug = False
        if debug: print(">>readNextEndLine")
        line = b_("")
        while True:
            # Prevent infinite loops in malformed PDFs
            if stream.tell() == 0:
                raise utils.PdfReadError("Could not read malformed PDF file")
            x = stream.read(1)
            if debug: print(("  x:", x, "%x" % ord(x)))
            if stream.tell() < 2:
                raise utils.PdfReadError("EOL marker not found")
            stream.seek(-2, 1)
            if x == b_('\n') or x == b_('\r'):  ## \n = LF; \r = CR
                crlf = False
                while x == b_('\n') or x == b_('\r'):
                    if debug:
                        if ord(x) == 0x0D:
                            print("  x is CR 0D")
                        elif ord(x) == 0x0A:
                            print("  x is LF 0A")
                    x = stream.read(1)
                    if x == b_('\n') or x == b_('\r'):  # account for CR+LF
                        stream.seek(-1, 1)
                        crlf = True
                    if stream.tell() < 2:
                        raise utils.PdfReadError("EOL marker not found")
                    stream.seek(-2, 1)
                stream.seek(2 if crlf else 1, 1)  # if using CR+LF, go back 2 bytes, else 1
                break
            else:
                if debug: print("  x is neither")
                line = x + line
                if debug: print(("  RNEL line:", line))
        if debug: print("leaving RNEL")
        return line

    def decrypt(self, password):
        """
        When using an encrypted / secured PDF file with the PDF Standard
        encryption handler, this function will allow the file to be decrypted.
        It checks the given password against the document's user password and
        owner password, and then stores the resulting decryption key if either
        password is correct.

        It does not matter which password was matched.  Both passwords provide
        the correct decryption key that will allow the document to be used with
        this library.

        :param str password: The password to match.
        :return: ``0`` if the password failed, ``1`` if the password matched the user
            password, and ``2`` if the password matched the owner password.
        :rtype: int
        :raises NotImplementedError: if document uses an unsupported encryption
            method.
        """

        self._override_encryption = True
        try:
            return self._decrypt(password)
        finally:
            self._override_encryption = False

    def _decrypt(self, password):
        encrypt = self.trailer['/Encrypt'].getObject()
        if encrypt['/Filter'] != '/Standard':
            raise NotImplementedError("only Standard PDF encryption handler is available")
        if not (encrypt['/V'] in (1, 2)):
            raise NotImplementedError(
                "only algorithm code 1 and 2 are supported. This PDF uses code %s" % encrypt['/V'])
        user_password, key = self._authenticateUserPassword(password)
        if user_password:
            self._decryption_key = key
            return 1
        else:
            rev = encrypt['/R'].getObject()
            if rev == 2:
                keylen = 5
            else:
                keylen = encrypt['/Length'].getObject() // 8
            key = _alg33_1(password, rev, keylen)
            real_O = encrypt["/O"].getObject()
            if rev == 2:
                userpass = utils.RC4_encrypt(key, real_O)
            else:
                val = real_O
                for i in range(19, -1, -1):
                    new_key = b_('')
                    for l in range(len(key)):
                        new_key += b_(chr(utils.ord_(key[l]) ^ i))
                    val = utils.RC4_encrypt(new_key, val)
                userpass = val
            owner_password, key = self._authenticateUserPassword(userpass)
            if owner_password:
                self._decryption_key = key
                return 2
        return 0

    def _authenticateUserPassword(self, password):
        encrypt = self.trailer['/Encrypt'].getObject()
        rev = encrypt['/R'].getObject()
        owner_entry = encrypt['/O'].getObject()
        p_entry = encrypt['/P'].getObject()
        id_entry = self.trailer['/ID'].getObject()
        id1_entry = id_entry[0].getObject()
        real_U = encrypt['/U'].getObject().original_bytes
        if rev == 2:
            U, key = _alg34(password, owner_entry, p_entry, id1_entry)
        elif rev >= 3:
            U, key = _alg35(password, rev,
                            encrypt["/Length"].getObject() // 8, owner_entry,
                            p_entry, id1_entry,
                            encrypt.get("/EncryptMetadata", BooleanObject(False)).getObject())
            U, real_U = U[:16], real_U[:16]
        return U == real_U, key

    def getIsEncrypted(self):
        return "/Encrypt" in self.trailer

    isEncrypted = property(lambda self: self.getIsEncrypted(), None, None)
    """
    Read-only boolean property showing whether this PDF file is encrypted.
    Note that this property, if true, will remain true even after the
    :meth:`decrypt()<PdfFileReader.decrypt>` method is called.
    """


def getRectangle(self, name, defaults):
    retval = self.get(name)
    if isinstance(retval, RectangleObject):
        return retval
    if retval is None:
        for d in defaults:
            retval = self.get(d)
            if retval is not None:
                break
    if isinstance(retval, IndirectObject):
        retval = self.pdf.getObject(retval)
    retval = RectangleObject(retval)
    setRectangle(self, name, retval)
    return retval


def setRectangle(self, name, value):
    if not isinstance(name, NameObject):
        name = NameObject(name)
    self[name] = value


def deleteRectangle(self, name):
    del self[name]


def createRectangleAccessor(name, fallback):
    return \
        property(
            lambda self: getRectangle(self, name, fallback),
            lambda self, value: setRectangle(self, name, value),
            lambda self: deleteRectangle(self, name)
        )


