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

import uuid
from hashlib import md5

from .content_stream import ContentStream
from .generic import *
from .page_object import PageObject
from .utils import _alg33, _alg34, _alg35
from .utils import isString, b_, u_


class PdfFileWriter(object):
    """
    This class supports writing PDF files out, given pages produced by another
    class (typically :class:`PdfFileReader<PdfFileReader>`).
    """

    def __init__(self):
        self._header = b_("%PDF-1.3")
        self._objects = []  # array of indirect objects

        # The root of our page tree node.
        pages = DictionaryObject()
        pages.update({
            NameObject("/Type"): NameObject("/Pages"),
            NameObject("/Count"): NumberObject(0),
            NameObject("/Kids"): ArrayObject(),
        })
        self._pages = self._addObject(pages)

        # info object
        info = DictionaryObject()
        info.update({
            NameObject("/Producer"): createStringObject(codecs.BOM_UTF16_BE + u_("PyPDF2").encode('utf-16be'))
        })
        self._info = self._addObject(info)

        # root object
        root = DictionaryObject()
        root.update({
            NameObject("/Type"): NameObject("/Catalog"),
            NameObject("/Pages"): self._pages,
        })
        self._root = None
        self._root_object = root

    def _addObject(self, obj):
        self._objects.append(obj)
        return IndirectObject(len(self._objects), 0, self)

    def getObject(self, ido):
        if ido.pdf != self:
            raise ValueError("pdf must be self")
        return self._objects[ido.idnum - 1]

    def _addPage(self, page, action):
        assert page["/Type"] == "/Page"
        page[NameObject("/Parent")] = self._pages
        page = self._addObject(page)
        pages = self.getObject(self._pages)
        action(pages["/Kids"], page)
        pages[NameObject("/Count")] = NumberObject(pages["/Count"] + 1)

    def addPage(self, page):
        """
        Adds a page to this PDF file.  The page is usually acquired from a
        :class:`PdfFileReader<PdfFileReader>` instance.

        :param PageObject page: The page to add to the document. Should be
            an instance of :class:`PageObject<PyPDF2.pdf.PageObject>`
        """
        self._addPage(page, list.append)

    def insertPage(self, page, index=0):
        """
        Insert a page in this PDF file. The page is usually acquired from a
        :class:`PdfFileReader<PdfFileReader>` instance.

        :param PageObject page: The page to add to the document.  This
            argument should be an instance of :class:`PageObject<pdf.PageObject>`.
        :param int index: Position at which the page will be inserted.
        """
        self._addPage(page, lambda l, p: l.insert(index, p))

    def getPage(self, pageNumber):
        """
        Retrieves a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: the page at the index given by *pageNumber*
        :rtype: :class:`PageObject<pdf.PageObject>`
        """
        pages = self.getObject(self._pages)
        # XXX: crude hack
        return pages["/Kids"][pageNumber].getObject()

    def getNumPages(self):
        """
        :return: the number of pages.
        :rtype: int
        """
        pages = self.getObject(self._pages)
        return int(pages[NameObject("/Count")])

    def addBlankPage(self, width=None, height=None):
        """
        Appends a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :return: the newly appended page
        :rtype: :class:`PageObject<PyPDF2.pdf.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        page = PageObject.createBlankPage(self, width, height)
        self.addPage(page)
        return page

    def insertBlankPage(self, width=None, height=None, index=0):
        """
        Inserts a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :param int index: Position to add the page.
        :return: the newly appended page
        :rtype: :class:`PageObject<PyPDF2.pdf.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        if width is None or height is None and \
                (self.getNumPages() - 1) >= index:
            oldpage = self.getPage(index)
            width = oldpage.mediaBox.getWidth()
            height = oldpage.mediaBox.getHeight()
        page = PageObject.createBlankPage(self, width, height)
        self.insertPage(page, index)
        return page

    def addJS(self, javascript):
        """
        Add Javascript which will launch upon opening this PDF.

        :param str javascript: Your Javascript.

        # >>> output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        # Example: This will launch the print window when the PDF is opened.
        """
        js = DictionaryObject()
        js.update({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): NameObject("(%s)" % javascript)
        })
        js_indirect_object = self._addObject(js)

        # We need a name for parameterized javascript in the pdf file, but it can be anything.
        js_string_name = str(uuid.uuid4())

        js_name_tree = DictionaryObject()
        js_name_tree.update({
            NameObject("/JavaScript"): DictionaryObject({
                NameObject("/Names"): ArrayObject([createStringObject(js_string_name), js_indirect_object])
            })
        })
        self._addObject(js_name_tree)

        self._root_object.update({
            NameObject("/OpenAction"): js_indirect_object,
            NameObject("/Names"): js_name_tree
        })

    def addAttachment(self, fname, fdata):
        """
        Embed a file inside the PDF.

        :param str fname: The filename to display.
        :param str fdata: The data in the file.
      
        Reference:
        https://www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
        Section 7.11.3
        """

        # We need 3 entries:
        # * The file's data
        # * The /Filespec entry
        # * The file's name, which goes in the Catalog

        # The entry for the file
        """ Sample:
        8 0 obj
        <<
         /Length 12
         /Type /EmbeddedFile
        >>
        stream
        Hello world!
        endstream
        endobj        
        """
        file_entry = DecodedStreamObject()
        file_entry.setData(fdata)
        file_entry.update({
            NameObject("/Type"): NameObject("/EmbeddedFile")
        })

        # The Filespec entry
        """ Sample:
        7 0 obj
        <<
         /Type /Filespec
         /F (hello.txt)
         /EF << /F 8 0 R >>
        >>
        """
        efEntry = DictionaryObject()
        efEntry.update({NameObject("/F"): file_entry})

        filespec = DictionaryObject()
        filespec.update({
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): createStringObject(fname),  # Perhaps also try TextStringObject
            NameObject("/EF"): efEntry
        })

        # Then create the entry for the root, as it needs a reference to the Filespec
        """ Sample:
        1 0 obj
        <<
         /Type /Catalog
         /Outlines 2 0 R
         /Pages 3 0 R
         /Names << /EmbeddedFiles << /Names [(hello.txt) 7 0 R] >> >>
        >>
        endobj
        
        """
        embeddedFilesNamesDictionary = DictionaryObject()
        embeddedFilesNamesDictionary.update({
            NameObject("/Names"): ArrayObject([createStringObject(fname), filespec])
        })

        embeddedFilesDictionary = DictionaryObject()
        embeddedFilesDictionary.update({
            NameObject("/EmbeddedFiles"): embeddedFilesNamesDictionary
        })
        # Update the root
        self._root_object.update({
            NameObject("/Names"): embeddedFilesDictionary
        })

    def appendPagesFromReader(self, reader, after_page_append=None):
        """
        Copy pages from reader to writer. Includes an optional callback parameter
        which is invoked after pages are appended to the writer.
        
        :param after_page_append:
        :param reader: a PdfFileReader object from which to copy page
            annotations to this writer object.  The writer's annots
        will then be updated
        :callback after_page_append (function): Callback function that is invoked after
            each page is appended to the writer. Callback signature:

        """
        # Get page count from writer and reader
        reader_num_pages = reader.getNumPages()
        writer_num_pages = self.getNumPages()

        # Copy pages from reader to writer
        for rpagenum in range(0, reader_num_pages):
            reader_page = reader.getPage(rpagenum)
            self.addPage(reader_page)
            writer_page = self.getPage(writer_num_pages + rpagenum)
            # Trigger callback, pass writer page as parameter
            if callable(after_page_append): after_page_append(writer_page)

    def updatePageFormFieldValues(self, page, fields):
        """
        Update the form field values for a given page from a fields dictionary.
        Copy field texts and values from fields to page.

        :param page: Page reference from PDF writer where the annotations
            and field data will be updated.
        :param fields: a Python dictionary of field names (/T) and text
            values (/V)
        """
        # Iterate through pages, update field values
        for j in range(0, len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()
            for field in fields:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/V"): TextStringObject(fields[field])
                    })

    def cloneReaderDocumentRoot(self, reader):
        """
        Copy the reader document root to the writer.

        :param reader:  PdfFileReader from the document root should be copied.
        :callback after_page_append
        """
        self._root_object = reader.trailer['/Root']

    def cloneDocumentFromReader(self, reader, after_page_append=None):
        """
        Create a copy (clone) of a document from a PDF file reader

        :param after_page_append:
        :param reader: PDF file reader instance from which the clone
            should be created.
        :callback after_page_append (function): Callback function that is invoked after
            each page is appended to the writer. Signature includes a reference to the
            appended page (delegates to appendPagesFromReader). Callback signature:

        """
        self.cloneReaderDocumentRoot(reader)
        self.appendPagesFromReader(reader, after_page_append)

    def encrypt(self, user_pwd, owner_pwd=None, use_128bit=True):
        """
        Encrypt this PDF file with the PDF Standard encryption handler.

        :param str user_pwd: The "user password", which allows for opening
            and reading the PDF file with the restrictions provided.
        :param str owner_pwd: The "owner password", which allows for
            opening the PDF files without any restrictions.  By default,
            the owner password is the same as the user password.
        :param bool use_128bit: flag as to whether to use 128bit
            encryption.  When false, 40bit encryption will be used.  By default,
            this flag is on.
        """
        import time, random
        if owner_pwd is None:
            owner_pwd = user_pwd
        if use_128bit:
            V = 2
            rev = 3
            keylen = int(128 / 8)
        else:
            V = 1
            rev = 2
            keylen = int(40 / 8)
        # permit everything:
        P = -1
        O = ByteStringObject(_alg33(owner_pwd, user_pwd, rev, keylen))
        ID_1 = ByteStringObject(md5(b_(repr(time.time()))).digest())
        ID_2 = ByteStringObject(md5(b_(repr(random.random()))).digest())
        self._ID = ArrayObject((ID_1, ID_2))
        if rev == 2:
            U, key = _alg34(user_pwd, O, P, ID_1)
        else:
            assert rev == 3
            U, key = _alg35(user_pwd, rev, keylen, O, P, ID_1, False)
        encrypt = DictionaryObject()
        encrypt[NameObject("/Filter")] = NameObject("/Standard")
        encrypt[NameObject("/V")] = NumberObject(V)
        if V == 2:
            encrypt[NameObject("/Length")] = NumberObject(keylen * 8)
        encrypt[NameObject("/R")] = NumberObject(rev)
        encrypt[NameObject("/O")] = ByteStringObject(O)
        encrypt[NameObject("/U")] = ByteStringObject(U)
        encrypt[NameObject("/P")] = NumberObject(P)
        self._encrypt = self._addObject(encrypt)
        self._encrypt_key = key

    def write(self, stream):
        """
        Writes the collection of pages added to this object out as a PDF file.

        :param stream: An object to write the file to.  The object must support
            the write method and the tell method, similar to a file object.
        """
        if hasattr(stream, 'mode') and 'b' not in stream.mode:
            warnings.warn(
                "File <%s> to write to is not in binary mode. It may not be written to correctly." % stream.name)
        debug = False
        import struct

        if not self._root:
            self._root = self._addObject(self._root_object)

        externalReferenceMap = {}

        # PDF objects sometimes have circular references to their /Page objects
        # inside their object tree (for example, annotations).  Those will be
        # indirect references to objects that we've recreated in this PDF.  To
        # address this problem, PageObject's store their original object
        # reference number, and we add it to the external reference map before
        # we sweep for indirect references.  This forces self-page-referencing
        # trees to reference the correct new object location, rather than
        # copying in a new copy of the page object.
        for objIndex in range(len(self._objects)):
            obj = self._objects[objIndex]
            if isinstance(obj, PageObject) and obj.indirectRef is not None:
                data = obj.indirectRef
                if data.pdf not in externalReferenceMap:
                    externalReferenceMap[data.pdf] = {}
                if data.generation not in externalReferenceMap[data.pdf]:
                    externalReferenceMap[data.pdf][data.generation] = {}
                externalReferenceMap[data.pdf][data.generation][data.idnum] = IndirectObject(objIndex + 1, 0, self)

        self.stack = []
        if debug: print(("ERM:", externalReferenceMap, "root:", self._root))
        self._sweepIndirectReferences(externalReferenceMap, self._root)
        del self.stack

        # Begin writing:
        object_positions = []
        stream.write(self._header + b_("\n"))
        stream.write(b_("%\xE2\xE3\xCF\xD3\n"))
        for i in range(len(self._objects)):
            idnum = (i + 1)
            obj = self._objects[i]
            object_positions.append(stream.tell())
            stream.write(b_(str(idnum) + " 0 obj\n"))
            key = None
            if hasattr(self, "_encrypt") and idnum != self._encrypt.idnum:
                pack1 = struct.pack("<i", i + 1)[:3]
                pack2 = struct.pack("<i", 0)[:2]
                key = self._encrypt_key + pack1 + pack2
                assert len(key) == (len(self._encrypt_key) + 5)
                md5_hash = md5(key).digest()
                key = md5_hash[:min(16, len(self._encrypt_key) + 5)]
            obj.writeToStream(stream, key)
            stream.write(b_("\nendobj\n"))

        # xref table
        xref_location = stream.tell()
        stream.write(b_("xref\n"))
        stream.write(b_("0 %s\n" % (len(self._objects) + 1)))
        stream.write(b_("%010d %05d f \n" % (0, 65535)))
        for offset in object_positions:
            stream.write(b_("%010d %05d n \n" % (offset, 0)))

        # trailer
        stream.write(b_("trailer\n"))
        trailer = DictionaryObject()
        trailer.update({
            NameObject("/Size"): NumberObject(len(self._objects) + 1),
            NameObject("/Root"): self._root,
            NameObject("/Info"): self._info,
        })
        if hasattr(self, "_ID"):
            trailer[NameObject("/ID")] = self._ID
        if hasattr(self, "_encrypt"):
            trailer[NameObject("/Encrypt")] = self._encrypt
        trailer.writeToStream(stream, None)

        # eof
        stream.write(b_("\nstartxref\n%s\n%%%%EOF\n" % xref_location))

    def addMetadata(self, infos):
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
        """
        args = {}
        for key, value in list(infos.items()):
            args[NameObject(key)] = createStringObject(value)
        self.getObject(self._info).update(args)

    def _sweepIndirectReferences(self, externMap, data):
        debug = False
        if debug: print((data, "TYPE", data.__class__.__name__))
        if isinstance(data, DictionaryObject):
            for key, value in list(data.items()):
                # noinspection PyUnusedLocal
                origvalue = value
                value = self._sweepIndirectReferences(externMap, value)
                if isinstance(value, StreamObject):
                    # a dictionary value is a stream.  streams must be indirect
                    # objects, so we need to change this value.
                    value = self._addObject(value)
                data[key] = value
            return data
        elif isinstance(data, ArrayObject):
            for i in range(len(data)):
                value = self._sweepIndirectReferences(externMap, data[i])
                if isinstance(value, StreamObject):
                    # an array value is a stream.  streams must be indirect
                    # objects, so we need to change this value
                    value = self._addObject(value)
                data[i] = value
            return data
        elif isinstance(data, IndirectObject):
            # internal indirect references are fine
            if data.pdf == self:
                if data.idnum in self.stack:
                    return data
                else:
                    self.stack.append(data.idnum)
                    realdata = self.getObject(data)
                    self._sweepIndirectReferences(externMap, realdata)
                    return data
            else:
                if data.pdf.stream.closed:
                    raise ValueError("I/O operation on closed file: {}".format(data.pdf.stream.name))
                newobj = externMap.get(data.pdf, {}).get(data.generation, {}).get(data.idnum, None)
                if newobj is None:
                    try:
                        newobj = data.pdf.getObject(data)
                        self._objects.append(None)  # placeholder
                        idnum = len(self._objects)
                        newobj_ido = IndirectObject(idnum, 0, self)
                        if data.pdf not in externMap:
                            externMap[data.pdf] = {}
                        if data.generation not in externMap[data.pdf]:
                            externMap[data.pdf][data.generation] = {}
                        externMap[data.pdf][data.generation][data.idnum] = newobj_ido
                        newobj = self._sweepIndirectReferences(externMap, newobj)
                        self._objects[idnum - 1] = newobj
                        return newobj_ido
                    except ValueError:
                        # Unable to resolve the Object, returning NullObject instead.
                        warnings.warn("Unable to resolve [{}: {}], returning NullObject instead".format(
                            data.__class__.__name__, data
                        ))
                        return NullObject()
                return newobj
        else:
            return data

    def getReference(self, obj):
        idnum = self._objects.index(obj) + 1
        ref = IndirectObject(idnum, 0, self)
        assert ref.getObject() == obj
        return ref

    def getOutlineRoot(self):
        if '/Outlines' in self._root_object:
            outline = self._root_object['/Outlines']
            idnum = self._objects.index(outline) + 1
            outlineRef = IndirectObject(idnum, 0, self)
            assert outlineRef.getObject() == outline
        else:
            outline = TreeObject()
            outline.update({})
            outlineRef = self._addObject(outline)
            self._root_object[NameObject('/Outlines')] = outlineRef

        return outline

    def getNamedDestRoot(self):
        if '/Names' in self._root_object and isinstance(self._root_object['/Names'], DictionaryObject):
            names = self._root_object['/Names']
            idnum = self._objects.index(names) + 1
            namesRef = IndirectObject(idnum, 0, self)
            assert namesRef.getObject() == names
            if '/Dests' in names and isinstance(names['/Dests'], DictionaryObject):
                dests = names['/Dests']
                idnum = self._objects.index(dests) + 1
                destsRef = IndirectObject(idnum, 0, self)
                assert destsRef.getObject() == dests
                if '/Names' in dests:
                    nd = dests['/Names']
                else:
                    nd = ArrayObject()
                    dests[NameObject('/Names')] = nd
            else:
                dests = DictionaryObject()
                destsRef = self._addObject(dests)
                names[NameObject('/Dests')] = destsRef
                nd = ArrayObject()
                dests[NameObject('/Names')] = nd

        else:
            names = DictionaryObject()
            namesRef = self._addObject(names)
            self._root_object[NameObject('/Names')] = namesRef
            dests = DictionaryObject()
            destsRef = self._addObject(dests)
            names[NameObject('/Dests')] = destsRef
            nd = ArrayObject()
            dests[NameObject('/Names')] = nd

        return nd

    def addBookmarkDestination(self, dest, parent=None):
        destRef = self._addObject(dest)

        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        parent = parent.getObject()
        # print parent.__class__.__name__
        parent.addChild(destRef, self)

        return destRef

    def addBookmarkDict(self, bookmark, parent=None):
        bookmarkObj = TreeObject()
        for k, v in list(bookmark.items()):
            bookmarkObj[NameObject(str(k))] = v
        bookmarkObj.update(bookmark)

        if '/A' in bookmark:
            action = DictionaryObject()
            for k, v in list(bookmark['/A'].items()):
                action[NameObject(str(k))] = v
            actionRef = self._addObject(action)
            bookmarkObj[NameObject('/A')] = actionRef

        bookmarkRef = self._addObject(bookmarkObj)

        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        parent = parent.getObject()
        parent.addChild(bookmarkRef, self)

        return bookmarkRef

    def addBookmark(self, title, pagenum, parent=None, color=None, bold=False, italic=False, fit='/Fit', *args):
        """
        Add a bookmark to this PDF file.

        :param str title: Title to use for this bookmark.
        :param int pagenum: Page number this bookmark will point to.
        :param parent: A reference to a parent bookmark to create nested
            bookmarks.
        :param tuple color: Color of the bookmark as a red, green, blue tuple
            from 0.0 to 1.0
        :param bool bold: Bookmark is bold
        :param bool italic: Bookmark is italic
        :param str fit: The fit of the destination page. See
            :meth:`addLink()<addLink>` for details.
        """
        pageRef = self.getObject(self._pages)['/Kids'][pagenum]
        action = DictionaryObject()
        zoomArgs = []
        for a in args:
            if a is not None:
                zoomArgs.append(NumberObject(a))
            else:
                zoomArgs.append(NullObject())
        dest = Destination(NameObject("/" + title + " bookmark"), pageRef, NameObject(fit), *zoomArgs)
        destArray = dest.getDestArray()
        action.update({
            NameObject('/D'): destArray,
            NameObject('/S'): NameObject('/GoTo')
        })
        actionRef = self._addObject(action)

        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        bookmark = TreeObject()

        bookmark.update({
            NameObject('/A'): actionRef,
            NameObject('/Title'): createStringObject(title),
        })

        if color is not None:
            bookmark.update({NameObject('/C'): ArrayObject([FloatObject(c) for c in color])})

        format = 0
        if italic:
            format += 1
        if bold:
            format += 2
        if format:
            bookmark.update({NameObject('/F'): NumberObject(format)})

        bookmarkRef = self._addObject(bookmark)

        parent = parent.getObject()
        parent.addChild(bookmarkRef, self)

        return bookmarkRef

    def addNamedDestinationObject(self, dest):
        destRef = self._addObject(dest)

        nd = self.getNamedDestRoot()
        nd.extend([dest['/Title'], destRef])

        return destRef

    def addNamedDestination(self, title, pagenum):
        pageRef = self.getObject(self._pages)['/Kids'][pagenum]
        dest = DictionaryObject()
        dest.update({
            NameObject('/D'): ArrayObject([pageRef, NameObject('/FitH'), NumberObject(826)]),
            NameObject('/S'): NameObject('/GoTo')
        })

        destRef = self._addObject(dest)
        nd = self.getNamedDestRoot()

        nd.extend([title, destRef])

        return destRef

    def removeLinks(self):
        """
        Removes links and annotations from this output.
        """
        pages = self.getObject(self._pages)['/Kids']
        for page in pages:
            pageRef = self.getObject(page)
            if "/Annots" in pageRef:
                del pageRef['/Annots']

    def removeImages(self, ignoreByteStringObject=False):
        """
        Removes images from this output.

        :param bool ignoreByteStringObject: optional parameter
            to ignore ByteString Objects.
        """
        pages = self.getObject(self._pages)['/Kids']
        for j in range(len(pages)):
            page = pages[j]
            pageRef = self.getObject(page)
            content = pageRef['/Contents'].getObject()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, pageRef)

            _operations = []
            seq_graphics = False
            for operands, operator in content.operations:
                if operator == b_('Tj'):
                    text = operands[0]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_("'"):
                    text = operands[0]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if ignoreByteStringObject:
                            if not isinstance(operands[0][i], TextStringObject):
                                operands[0][i] = TextStringObject()

                if operator == b_('q'):
                    seq_graphics = True
                if operator == b_('Q'):
                    seq_graphics = False
                if seq_graphics:
                    if operator in [b_('cm'), b_('w'), b_('J'), b_('j'), b_('M'), b_('d'), b_('ri'), b_('i'),
                                    b_('gs'), b_('W'), b_('b'), b_('s'), b_('S'), b_('f'), b_('F'), b_('n'), b_('m'),
                                    b_('l'),
                                    b_('c'), b_('v'), b_('y'), b_('h'), b_('B'), b_('Do'), b_('sh')]:
                        continue
                if operator == b_('re'):
                    continue
                _operations.append((operands, operator))

            content.operations = _operations
            pageRef.__setitem__(NameObject('/Contents'), content)

    def removeText(self, ignoreByteStringObject=False):
        """
        Removes images from this output.

        :param bool ignoreByteStringObject: optional parameter
            to ignore ByteString Objects.
        """
        pages = self.getObject(self._pages)['/Kids']
        for j in range(len(pages)):
            page = pages[j]
            pageRef = self.getObject(page)
            content = pageRef['/Contents'].getObject()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, pageRef)
            for operands, operator in content.operations:
                if operator == b_('Tj'):
                    text = operands[0]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_("'"):
                    text = operands[0]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[2] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if not ignoreByteStringObject:
                            if isinstance(operands[0][i], TextStringObject):
                                operands[0][i] = TextStringObject()
                        else:
                            if isinstance(operands[0][i], TextStringObject) or \
                                    isinstance(operands[0][i], ByteStringObject):
                                operands[0][i] = TextStringObject()

            pageRef.__setitem__(NameObject('/Contents'), content)

    def addURI(self, pagenum, uri, rect, border=None):
        """
        Add an URI from a rectangular area to the specified page.
        This uses the basic structure of AddLink

        :param int pagenum: index of the page on which to place the URI action.
        :param int uri: string -- uri of resource to link to.
        :param rect: :class:`RectangleObject<PyPDF2.generic.RectangleObject>` or array of four
            integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be
            drawn if this argument is omitted.

        REMOVED FIT/ZOOM ARG
        -John Mulligan
        """

        pageLink = self.getObject(self._pages)['/Kids'][pagenum]
        pageRef = self.getObject(pageLink)

        if border is not None:
            borderArr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dashPattern = ArrayObject([NameObject(n) for n in border[3]])
                borderArr.append(dashPattern)
        else:
            borderArr = [NumberObject(2)] * 3

        if isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        lnk2 = DictionaryObject()
        lnk2.update({
            NameObject('/S'): NameObject('/URI'),
            NameObject('/URI'): TextStringObject(uri)
        })
        lnk = DictionaryObject()
        lnk.update({
            NameObject('/Type'): NameObject('/Annot'),
            NameObject('/Subtype'): NameObject('/Link'),
            NameObject('/P'): pageLink,
            NameObject('/Rect'): rect,
            NameObject('/H'): NameObject('/I'),
            NameObject('/Border'): ArrayObject(borderArr),
            NameObject('/A'): lnk2
        })
        lnkRef = self._addObject(lnk)

        if "/Annots" in pageRef:
            pageRef['/Annots'].append(lnkRef)
        else:
            pageRef[NameObject('/Annots')] = ArrayObject([lnkRef])

    def addLink(self, pagenum, pagedest, rect, border=None, fit='/Fit', *args):
        """
        Add an internal link from a rectangular area to the specified page.

        :param int pagenum: index of the page on which to place the link.
        :param int pagedest: index of the page to which the link should go.
        :param rect: :class:`RectangleObject<PyPDF2.generic.RectangleObject>` or array of four
            integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be
            drawn if this argument is omitted.
        :param str fit: Page fit or 'zoom' option (see below). Additional arguments may need
            to be supplied. Passing ``None`` will be read as a null value for that coordinate.

        Valid zoom arguments (see Table 8.2 of the PDF 1.7 reference for details):
             /Fit       No additional arguments
             /XYZ       [left] [top] [zoomFactor]
             /FitH      [top]
             /FitV      [left]
             /FitR      [left] [bottom] [right] [top]
             /FitB      No additional arguments
             /FitBH     [top]
             /FitBV     [left]
        """

        pageLink = self.getObject(self._pages)['/Kids'][pagenum]
        pageDest = self.getObject(self._pages)['/Kids'][pagedest]  # TODO: switch for external link
        pageRef = self.getObject(pageLink)

        if border is not None:
            borderArr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dashPattern = ArrayObject([NameObject(n) for n in border[3]])
                borderArr.append(dashPattern)
        else:
            borderArr = [NumberObject(0)] * 3

        if isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        zoomArgs = []
        for a in args:
            if a is not None:
                zoomArgs.append(NumberObject(a))
            else:
                zoomArgs.append(NullObject())
        dest = Destination(NameObject("/LinkName"), pageDest, NameObject(fit),
                           *zoomArgs)  # TODO: create a better name for the link
        destArray = dest.getDestArray()

        lnk = DictionaryObject()
        lnk.update({
            NameObject('/Type'): NameObject('/Annot'),
            NameObject('/Subtype'): NameObject('/Link'),
            NameObject('/P'): pageLink,
            NameObject('/Rect'): rect,
            NameObject('/Border'): ArrayObject(borderArr),
            NameObject('/Dest'): destArray
        })
        lnkRef = self._addObject(lnk)

        if "/Annots" in pageRef:
            pageRef['/Annots'].append(lnkRef)
        else:
            pageRef[NameObject('/Annots')] = ArrayObject([lnkRef])

    _valid_layouts = ['/NoLayout', '/SinglePage', '/OneColumn', '/TwoColumnLeft', '/TwoColumnRight', '/TwoPageLeft',
                      '/TwoPageRight']

    def getPageLayout(self):
        """
        Get the page layout.
        See :meth:`setPageLayout()<PdfFileWriter.setPageLayout>` for a description of valid layouts.

        :return: Page layout currently being used.
        :rtype: str, None if not specified
        """
        try:
            return self._root_object['/PageLayout']
        except KeyError:
            return None

    def setPageLayout(self, layout):
        """
        Set the page layout

        :param str layout: The page layout to be used

        Valid layouts are:
             /NoLayout        Layout explicitly not specified
             /SinglePage      Show one page at a time
             /OneColumn       Show one column at a time
             /TwoColumnLeft   Show pages in two columns, odd-numbered pages on the left
             /TwoColumnRight  Show pages in two columns, odd-numbered pages on the right
             /TwoPageLeft     Show two pages at a time, odd-numbered pages on the left
             /TwoPageRight    Show two pages at a time, odd-numbered pages on the right
        """
        if not isinstance(layout, NameObject):
            if layout not in self._valid_layouts:
                warnings.warn("Layout should be one of: {}".format(', '.join(self._valid_layouts)))
            layout = NameObject(layout)
        self._root_object.update({NameObject('/PageLayout'): layout})

    pageLayout = property(getPageLayout, setPageLayout)
    """Read and write property accessing the :meth:`getPageLayout()<PdfFileWriter.getPageLayout>`
    and :meth:`setPageLayout()<PdfFileWriter.setPageLayout>` methods."""

    _valid_modes = ['/UseNone', '/UseOutlines', '/UseThumbs', '/FullScreen', '/UseOC', '/UseAttachments']

    def getPageMode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfFileWriter.setPageMode>` for a description
        of valid modes.

        :return: Page mode currently being used.
        :rtype: str, None if not specified
        """
        try:
            return self._root_object['/PageMode']
        except KeyError:
            return None

    def setPageMode(self, mode):
        """
        Set the page mode.

        :param str mode: The page mode to use.

        Valid modes are:
            /UseNone         Do not show outlines or thumbnails panels
            /UseOutlines     Show outlines (aka bookmarks) panel
            /UseThumbs       Show page thumbnails panel
            /FullScreen      Fullscreen view
            /UseOC           Show Optional Content Group (OCG) panel
            /UseAttachments  Show attachments panel
        """
        if not isinstance(mode, NameObject):
            if mode not in self._valid_modes:
                warnings.warn("Mode should be one of: {}".format(', '.join(self._valid_modes)))
            mode = NameObject(mode)
        self._root_object.update({NameObject('/PageMode'): mode})

    pageMode = property(getPageMode, setPageMode)
    """Read and write property accessing the :meth:`getPageMode()<PdfFileWriter.getPageMode>`
    and :meth:`setPageMode()<PdfFileWriter.setPageMode>` methods."""
