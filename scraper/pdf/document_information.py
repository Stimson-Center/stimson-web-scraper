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

__maintainer__ = "Phaseit, Inc."
__maintainer_email = "PyPDF2@phaseit.net"

from .generic import *


class DocumentInformation(DictionaryObject):
    """
    A class representing the basic document metadata provided in a PDF File.
    This class is accessible through
    :meth:`getDocumentInfo()<PyPDF2.PdfFileReader.getDocumentInfo()>`

    All text properties of the document metadata have
    *two* properties, eg. author and author_raw. The non-raw property will
    always return a ``TextStringObject``, making it ideal for a case where
    the metadata is being displayed. The raw property can sometimes return
    a ``ByteStringObject``, if PyPDF2 was unable to decode the string's
    text encoding; this requires additional safety in the caller and
    therefore is not as commonly accessed.
    """

    def __init__(self):
        DictionaryObject.__init__(self)

    def getText(self, key):
        retval = self.get(key, None)
        if isinstance(retval, TextStringObject):
            return retval
        return None

    title = property(lambda self: self.getText("/Title"))
    """Read-only property accessing the document's **title**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the title is not specified."""
    title_raw = property(lambda self: self.get("/Title"))
    """The "raw" version of title; can return a ``ByteStringObject``."""

    author = property(lambda self: self.getText("/Author"))
    """Read-only property accessing the document's **author**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the author is not specified."""
    author_raw = property(lambda self: self.get("/Author"))
    """The "raw" version of author; can return a ``ByteStringObject``."""

    subject = property(lambda self: self.getText("/Subject"))
    """Read-only property accessing the document's **subject**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the subject is not specified."""
    subject_raw = property(lambda self: self.get("/Subject"))
    """The "raw" version of subject; can return a ``ByteStringObject``."""

    creator = property(lambda self: self.getText("/Creator"))
    """Read-only property accessing the document's **creator**. If the
    document was converted to PDF from another format, this is the name of the
    application (e.g. OpenOffice) that created the original document from
    which it was converted. Returns a unicode string (``TextStringObject``)
    or ``None`` if the creator is not specified."""
    creator_raw = property(lambda self: self.get("/Creator"))
    """The "raw" version of creator; can return a ``ByteStringObject``."""

    producer = property(lambda self: self.getText("/Producer"))
    """Read-only property accessing the document's **producer**.
    If the document was converted to PDF from another format, this is
    the name of the application (for example, OSX Quartz) that converted
    it to PDF. Returns a unicode string (``TextStringObject``)
    or ``None`` if the producer is not specified."""
    producer_raw = property(lambda self: self.get("/Producer"))
    """The "raw" version of producer; can return a ``ByteStringObject``."""

    creation_date = property(lambda self: self.getText("/CreationDate").replace("D:", ""))
    """Read-only property accessing the document's **create_date**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the creation_date is not specified."""
    creation_date_raw = property(lambda self: self.get("/CreationDate"))
    """The "raw" version of creation_date; can return a ``ByteStringObject``."""
