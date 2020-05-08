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

__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

from .generic import *
# from .utils import b_, ord_, str_

"""
Utility functions for PDF library.
"""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

import builtins
import sys
import struct
from hashlib import md5

xrange_fn = getattr(builtins, "xrange", range)
_basestring = getattr(builtins, "basestring", str)

bytes_type = type(bytes())  # Works the same in Python 2.X and 3.X
string_type = getattr(builtins, "unicode", str)
int_types = (int,)


# Make basic type tests more consistent
def isString(s):
    """Test if arg is a string. Compatible with Python 2 and 3."""
    return isinstance(s, _basestring)


def isInt(n):
    """Test if arg is an int. Compatible with Python 2 and 3."""
    return isinstance(n, int_types)


def isBytes(b):
    """Test if arg is a bytes instance. Compatible with Python 2 and 3."""
    return isinstance(b, bytes_type)


# custom implementation of warnings.formatwarning
def formatWarning(message, category, filename, lineno, line=None):
    file = filename.replace("/", "\\").rsplit("\\", 1)[1]  # find the file name
    return "%s: %s [%s:%s]\n" % (category.__name__, message, file, lineno)


def readUntilWhitespace(stream, maxchars=None):
    """
    Reads non-whitespace characters and returns them.
    Stops upon encountering whitespace or when maxchars is reached.
    """
    txt = b_("")
    while True:
        tok = stream.read(1)
        if tok.isspace() or not tok:
            break
        txt += tok
        if len(txt) == maxchars:
            break
    return txt


def readNonWhitespace(stream):
    """
    Finds and reads the next non-whitespace character (ignores whitespace).
    """
    tok = WHITESPACES[0]
    while tok in WHITESPACES:
        tok = stream.read(1)
    return tok


def skipOverWhitespace(stream):
    """
    Similar to readNonWhitespace, but returns a Boolean if more than
    one whitespace character was read.
    """
    tok = WHITESPACES[0]
    cnt = 0
    while tok in WHITESPACES:
        tok = stream.read(1)
        cnt += 1
    return cnt > 1


def skipOverComment(stream):
    tok = stream.read(1)
    stream.seek(-1, 1)
    if tok == b_('%'):
        while tok not in (b_('\n'), b_('\r')):
            tok = stream.read(1)


def readUntilRegex(stream, regex, ignore_eof=False):
    """
    Reads until the regular expression pattern matched (ignore the match)
    Raise PdfStreamError on premature end-of-file.
    :param bool ignore_eof: If true, ignore end-of-line and return immediately
    """
    name = b_('')
    while True:
        tok = stream.read(16)
        if not tok:
            # stream has truncated prematurely
            if ignore_eof:
                return name
            else:
                raise PdfStreamError("Stream has ended unexpectedly")
        m = regex.search(tok)
        if m is not None:
            name += tok[:m.start()]
            stream.seek(m.start() - len(tok), 1)
            break
        name += tok
    return name


class ConvertFunctionsToVirtualList(object):
    def __init__(self, lengthFunction, getFunction):
        self.lengthFunction = lengthFunction
        self.getFunction = getFunction

    def __len__(self):
        return self.lengthFunction()

    def __getitem__(self, index):
        if isinstance(index, slice):
            indices = xrange_fn(*index.indices(len(self)))
            cls = type(self)
            return cls(indices.__len__, lambda idx: self[indices[idx]])
        if not isInt(index):
            raise TypeError("sequence indices must be integers")
        len_self = len(self)
        if index < 0:
            # support negative indexes
            index = len_self + index
        if index < 0 or index >= len_self:
            raise IndexError("sequence index out of range")
        return self.getFunction(index)


def RC4_encrypt(key, plaintext):
    S = [i for i in range(256)]
    j = 0
    for i in range(256):
        j = (j + S[i] + ord_(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]
    i, j = 0, 0
    retval = []
    for x in range(len(plaintext)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = S[(S[i] + S[j]) % 256]
        retval.append(b_(chr(ord_(plaintext[x]) ^ t)))
    return b_("").join(retval)


def matrixMultiply(a, b):
    return [[sum([float(i) * float(j)
                  for i, j in zip(row, col)]
                 ) for col in zip(*b)]
            for row in a]


def markLocation(stream):
    """Creates text file showing current location in context."""
    # Mainly for debugging
    RADIUS = 5000
    stream.seek(-RADIUS, 1)
    outputDoc = open('PyPDF2_pdfLocation.txt', 'w')
    outputDoc.write(stream.read(RADIUS))
    outputDoc.write('HERE')
    outputDoc.write(stream.read(RADIUS))
    outputDoc.close()
    stream.seek(-RADIUS, 1)


class PyPdfError(Exception):
    pass


class PdfReadError(PyPdfError):
    pass


class PageSizeNotDefinedError(PyPdfError):
    pass


class PdfReadWarning(UserWarning):
    pass


class PdfStreamError(PdfReadError):
    pass


if sys.version_info[0] < 3:
    def b_(s):
        return s
else:
    B_CACHE = {}


    def b_(s):
        bc = B_CACHE
        if s in bc:
            return bc[s]
        if type(s) == bytes:
            return s
        else:
            if s is not None:
                r = s.encode('latin-1')
            else:
                r = ''
            if len(s) < 2:
                bc[s] = r
            return r


def u_(s):
    return s


def str_(b):
    if sys.version_info[0] < 3:
        return b
    else:
        if type(b) == bytes:
            return b.decode('latin-1')
        else:
            return b


def ord_(b):
    if sys.version_info[0] < 3 or type(b) == str:
        return ord(b)
    else:
        return b


def chr_(c):
    if sys.version_info[0] < 3:
        return c
    else:
        return chr(c)


def barray(b):
    if sys.version_info[0] < 3:
        return b
    else:
        return bytearray(b)


def hexencode(b):
    if sys.version_info[0] < 3:
        return b.encode('hex')
    else:
        import codecs
        coder = codecs.getencoder('hex_codec')
        return coder(b)[0]


def hexStr(num):
    return hex(num).replace('L', '')


WHITESPACES = [b_(x) for x in [' ', '\n', '\r', '\t', '\x00']]


def paethPredictor(left, up, up_left):
    p = left + up - up_left
    dist_left = abs(p - left)
    dist_up = abs(p - up)
    dist_up_left = abs(p - up_left)

    if dist_left <= dist_up and dist_left <= dist_up_left:
        return left
    elif dist_up <= dist_up_left:
        return up
    else:
        return up_left


def convertToInt(d, size):
    if size > 8:
        raise PdfReadError("invalid size in convertToInt")
    d = b_("\x00\x00\x00\x00\x00\x00\x00\x00") + b_(d)
    d = d[-8:]
    return struct.unpack(">q", d)[0]


# ref: pdf1.8 spec section 3.5.2 algorithm 3.2
_encryption_padding = b_('\x28\xbf\x4e\x5e\x4e\x75\x8a\x41\x64\x00\x4e\x56') + \
                      b_('\xff\xfa\x01\x08\x2e\x2e\x00\xb6\xd0\x68\x3e\x80\x2f\x0c') + \
                      b_('\xa9\xfe\x64\x53\x69\x7a')


# Implementation of algorithm 3.2 of the PDF standard security handler,
# section 3.5.2 of the PDF 1.6 reference.
def _alg32(password, rev, keylen, owner_entry, p_entry, id1_entry, metadata_encrypt=True):
    # 1. Pad or truncate the password string to exactly 32 bytes.  If the
    # password string is more than 32 bytes long, use only its first 32 bytes;
    # if it is less than 32 bytes long, pad it by appending the required number
    # of additional bytes from the beginning of the padding string
    # (_encryption_padding).
    password = b_((str_(password) + str_(_encryption_padding))[:32])
    # 2. Initialize the MD5 hash function and pass the result of step 1 as
    # input to this function.
    import struct
    m = md5(password)
    # 3. Pass the value of the encryption dictionary's /O entry to the MD5 hash
    # function.
    m.update(owner_entry.original_bytes)
    # 4. Treat the value of the /P entry as an unsigned 4-byte integer and pass
    # these bytes to the MD5 hash function, low-order byte first.
    p_entry = struct.pack('<i', p_entry)
    m.update(p_entry)
    # 5. Pass the first element of the file's file identifier array to the MD5
    # hash function.
    m.update(id1_entry.original_bytes)
    # 6. (Revision 3 or greater) If document metadata is not being encrypted,
    # pass 4 bytes with the value 0xFFFFFFFF to the MD5 hash function.
    if rev >= 3 and not metadata_encrypt:
        m.update(b_("\xff\xff\xff\xff"))
    # 7. Finish the hash.
    md5_hash = m.digest()
    # 8. (Revision 3 or greater) Do the following 50 times: Take the output
    # from the previous MD5 hash and pass the first n bytes of the output as
    # input into a new MD5 hash, where n is the number of bytes of the
    # encryption key as defined by the value of the encryption dictionary's
    # /Length entry.
    if rev >= 3:
        for i in range(50):
            md5_hash = md5(md5_hash[:keylen]).digest()
    # 9. Set the encryption key to the first n bytes of the output from the
    # final MD5 hash, where n is always 5 for revision 2 but, for revision 3 or
    # greater, depends on the value of the encryption dictionary's /Length
    # entry.
    return md5_hash[:keylen]


# Implementation of algorithm 3.3 of the PDF standard security handler,
# section 3.5.2 of the PDF 1.6 reference.
def _alg33(owner_pwd, user_pwd, rev, keylen):
    # steps 1 - 4
    key = _alg33_1(owner_pwd, rev, keylen)
    # 5. Pad or truncate the user password string as described in step 1 of
    # algorithm 3.2.
    user_pwd = b_((user_pwd + str_(_encryption_padding))[:32])
    # 6. Encrypt the result of step 5, using an RC4 encryption function with
    # the encryption key obtained in step 4.
    val = RC4_encrypt(key, user_pwd)
    # 7. (Revision 3 or greater) Do the following 19 times: Take the output
    # from the previous invocation of the RC4 function and pass it as input to
    # a new invocation of the function; use an encryption key generated by
    # taking each byte of the encryption key obtained in step 4 and performing
    # an XOR operation between that byte and the single-byte value of the
    # iteration counter (from 1 to 19).
    if rev >= 3:
        for i in range(1, 20):
            new_key = ''
            for l in range(len(key)):
                new_key += chr(ord_(key[l]) ^ i)
            val = RC4_encrypt(new_key, val)
    # 8. Store the output from the final invocation of the RC4 as the value of
    # the /O entry in the encryption dictionary.
    return val


# Steps 1-4 of algorithm 3.3
def _alg33_1(password, rev, keylen):
    # 1. Pad or truncate the owner password string as described in step 1 of
    # algorithm 3.2.  If there is no owner password, use the user password
    # instead.
    password = b_((password + str_(_encryption_padding))[:32])
    # 2. Initialize the MD5 hash function and pass the result of step 1 as
    # input to this function.
    m = md5(password)
    # 3. (Revision 3 or greater) Do the following 50 times: Take the output
    # from the previous MD5 hash and pass it as input into a new MD5 hash.
    md5_hash = m.digest()
    if rev >= 3:
        for i in range(50):
            md5_hash = md5(md5_hash).digest()
    # 4. Create an RC4 encryption key using the first n bytes of the output
    # from the final MD5 hash, where n is always 5 for revision 2 but, for
    # revision 3 or greater, depends on the value of the encryption
    # dictionary's /Length entry.
    key = md5_hash[:keylen]
    return key


# Implementation of algorithm 3.4 of the PDF standard security handler,
# section 3.5.2 of the PDF 1.6 reference.
def _alg34(password, owner_entry, p_entry, id1_entry):
    # 1. Create an encryption key based on the user password string, as
    # described in algorithm 3.2.
    key = _alg32(password, 2, 5, owner_entry, p_entry, id1_entry)
    # 2. Encrypt the 32-byte padding string shown in step 1 of algorithm 3.2,
    # using an RC4 encryption function with the encryption key from the
    # preceding step.
    U = RC4_encrypt(key, _encryption_padding)
    # 3. Store the result of step 2 as the value of the /U entry in the
    # encryption dictionary.
    return U, key


# Implementation of algorithm 3.4 of the PDF standard security handler,
# section 3.5.2 of the PDF 1.6 reference.
def _alg35(password, rev, keylen, owner_entry, p_entry, id1_entry, metadata_encrypt):
    # 1. Create an encryption key based on the user password string, as
    # described in Algorithm 3.2.
    key = _alg32(password, rev, keylen, owner_entry, p_entry, id1_entry)
    # 2. Initialize the MD5 hash function and pass the 32-byte padding string
    # shown in step 1 of Algorithm 3.2 as input to this function.
    m = md5()
    m.update(_encryption_padding)
    # 3. Pass the first element of the file's file identifier array (the value
    # of the ID entry in the document's trailer dictionary; see Table 3.13 on
    # page 73) to the hash function and finish the hash.  (See implementation
    # note 25 in Appendix H.)
    m.update(id1_entry.original_bytes)
    md5_hash = m.digest()
    # 4. Encrypt the 16-byte result of the hash, using an RC4 encryption
    # function with the encryption key from step 1.
    val = RC4_encrypt(key, md5_hash)
    # 5. Do the following 19 times: Take the output from the previous
    # invocation of the RC4 function and pass it as input to a new invocation
    # of the function; use an encryption key generated by taking each byte of
    # the original encryption key (obtained in step 2) and performing an XOR
    # operation between that byte and the single-byte value of the iteration
    # counter (from 1 to 19).
    for i in range(1, 20):
        new_key = b_('')
        for l in range(len(key)):
            new_key += b_(chr(ord_(key[l]) ^ i))
        val = RC4_encrypt(new_key, val)
    # 6. Append 16 bytes of arbitrary padding to the output from the final
    # invocation of the RC4 function and store the 32-byte result as the value
    # of the U entry in the encryption dictionary.
    # (implementator note: I don't know what "arbitrary padding" is supposed to
    # mean, so I have used null bytes.  This seems to match a few other
    # people's implementations)
    return val + (b_('\x00') * 16), key


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
