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

from io import BytesIO

from .generic import *
from .utils import b_, ord_
from .utils import readNonWhitespace


class ContentStream(DecodedStreamObject):
    # noinspection PyMissingConstructor
    def __init__(self, stream, pdf):
        # super().__init__() # crash in utils.py  def b_(s) when s in NoneType
        self.pdf = pdf
        self.operations = []
        # stream may be a StreamObject or an ArrayObject containing
        # multiple StreamObjects to be cat'd together.
        stream = stream.getObject()
        if isinstance(stream, ArrayObject):
            data = b_("")
            for s in stream:
                data += b_(s.getObject().getData())
            stream = BytesIO(b_(data))
        else:
            stream = BytesIO(b_(stream.getData()))
        self.__parseContentStream(stream)

    def __parseContentStream(self, stream):
        # file("f:\\tmp.txt", "w").write(stream.read())
        stream.seek(0, 0)
        operands = []
        while True:
            peek = readNonWhitespace(stream)
            if peek == b_('') or ord_(peek) == 0:
                break
            stream.seek(-1, 1)
            if peek.isalpha() or peek == b_("'") or peek == b_('"'):
                operator = utils.readUntilRegex(stream,
                                                NameObject.delimiterPattern, True)
                if operator == b_("BI"):
                    # begin inline image - a completely different parsing
                    # mechanism is required, of course... thanks buddy...
                    assert operands == []
                    ii = self._readInlineImage(stream)
                    self.operations.append((ii, b_("INLINE IMAGE")))
                else:
                    self.operations.append((operands, operator))
                    operands = []
            elif peek == b_('%'):
                # If we encounter a comment in the content stream, we have to
                # handle it here.  Typically, readObject will handle
                # encountering a comment -- but readObject assumes that
                # following the comment must be the object we're trying to
                # read.  In this case, it could be an operator instead.
                while peek not in (b_('\r'), b_('\n')):
                    peek = stream.read(1)
            else:
                operands.append(readObject(stream, None))

    def _readInlineImage(self, stream):
        # begin reading just after the "BI" - begin image
        # first read the dictionary of settings.
        settings = DictionaryObject()
        while True:
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            if tok == b_("I"):
                # "ID" - begin of image data
                break
            key = readObject(stream, self.pdf)
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            value = readObject(stream, self.pdf)
            settings[key] = value
        # left at beginning of ID
        tmp = stream.read(3)
        assert tmp[:2] == b_("ID")
        data = b_("")
        while True:
            # Read the inline image, while checking for EI (End Image) operator.
            tok = stream.read(1)
            if tok == b_("E"):
                # Check for End Image
                tok2 = stream.read(1)
                if tok2 == b_("I"):
                    # Data can contain EI, so check for the Q operator.
                    tok3 = stream.read(1)
                    info = tok + tok2
                    # We need to find whitespace between EI and Q.
                    has_q_whitespace = False
                    while tok3 in utils.WHITESPACES:
                        has_q_whitespace = True
                        info += tok3
                        tok3 = stream.read(1)
                    if tok3 == b_("Q") and has_q_whitespace:
                        stream.seek(-1, 1)
                        break
                    else:
                        stream.seek(-1, 1)
                        data += info
                else:
                    stream.seek(-1, 1)
                    data += tok
            else:
                data += tok
        return {"settings": settings, "data": data}

    def _getData(self):
        newdata = BytesIO()
        for operands, operator in self.operations:
            if operator == b_("INLINE IMAGE"):
                newdata.write(b_("BI"))
                dicttext = BytesIO()
                operands["settings"].writeToStream(dicttext, None)
                newdata.write(dicttext.getvalue()[2:-2])
                newdata.write(b_("ID "))
                newdata.write(operands["data"])
                newdata.write(b_("EI"))
            else:
                for op in operands:
                    op.writeToStream(newdata, None)
                    newdata.write(b_(" "))
                newdata.write(b_(operator))
            newdata.write(b_("\n"))
        return newdata.getvalue()

    def _setData(self, value):
        self.__parseContentStream(BytesIO(b_(value)))

    _data = property(_getData, _setData)
