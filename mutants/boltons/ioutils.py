# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# Coding decl above needed for rendering the emdash properly in the
# documentation.

"""
Module ``ioutils`` implements a number of helper classes and functions which
are useful when dealing with input, output, and bytestreams in a variety of
ways.
"""
import os
from io import BytesIO, IOBase
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)
from errno import EINVAL
from codecs import EncodedFile
from tempfile import TemporaryFile
from itertools import zip_longest

READ_CHUNK_SIZE = 21333
"""
Number of bytes to read at a time. The value is ~ 1/3rd of 64k which means that
the value will easily fit in the L2 cache of most processors even if every
codepoint in a string is three bytes long which makes it a nice fast default
value.
"""
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class SpooledIOBase(IOBase):
    """
    A base class shared by the SpooledBytesIO and SpooledStringIO classes.

    The SpooledTemporaryFile class is missing several attributes and methods
    present in the StringIO implementation. This brings the api as close to
    parity as possible so that classes derived from SpooledIOBase can be used
    as near drop-in replacements to save memory.
    """
    __metaclass__ = ABCMeta

    def xǁSpooledIOBaseǁ__init____mutmut_orig(self, max_size=5000000, dir=None):
        self._max_size = max_size
        self._dir = dir

    def xǁSpooledIOBaseǁ__init____mutmut_1(self, max_size=5000001, dir=None):
        self._max_size = max_size
        self._dir = dir

    def xǁSpooledIOBaseǁ__init____mutmut_2(self, max_size=5000000, dir=None):
        self._max_size = None
        self._dir = dir

    def xǁSpooledIOBaseǁ__init____mutmut_3(self, max_size=5000000, dir=None):
        self._max_size = max_size
        self._dir = None
    
    xǁSpooledIOBaseǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ__init____mutmut_1': xǁSpooledIOBaseǁ__init____mutmut_1, 
        'xǁSpooledIOBaseǁ__init____mutmut_2': xǁSpooledIOBaseǁ__init____mutmut_2, 
        'xǁSpooledIOBaseǁ__init____mutmut_3': xǁSpooledIOBaseǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ__init____mutmut_orig)
    xǁSpooledIOBaseǁ__init____mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ__init__'

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_orig(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError('I/O operation on closed file.'
                             if msg is None else msg)

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_1(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError(None)

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_2(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError('XXI/O operation on closed file.XX'
                             if msg is None else msg)

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_3(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError('i/o operation on closed file.'
                             if msg is None else msg)

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_4(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError('I/O OPERATION ON CLOSED FILE.'
                             if msg is None else msg)

    def xǁSpooledIOBaseǁ_checkClosed__mutmut_5(self, msg=None):
        """Raise a ValueError if file is closed"""
        if self.closed:
            raise ValueError('I/O operation on closed file.'
                             if msg is not None else msg)
    
    xǁSpooledIOBaseǁ_checkClosed__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ_checkClosed__mutmut_1': xǁSpooledIOBaseǁ_checkClosed__mutmut_1, 
        'xǁSpooledIOBaseǁ_checkClosed__mutmut_2': xǁSpooledIOBaseǁ_checkClosed__mutmut_2, 
        'xǁSpooledIOBaseǁ_checkClosed__mutmut_3': xǁSpooledIOBaseǁ_checkClosed__mutmut_3, 
        'xǁSpooledIOBaseǁ_checkClosed__mutmut_4': xǁSpooledIOBaseǁ_checkClosed__mutmut_4, 
        'xǁSpooledIOBaseǁ_checkClosed__mutmut_5': xǁSpooledIOBaseǁ_checkClosed__mutmut_5
    }
    
    def _checkClosed(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ_checkClosed__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ_checkClosed__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _checkClosed.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ_checkClosed__mutmut_orig)
    xǁSpooledIOBaseǁ_checkClosed__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ_checkClosed'
    @abstractmethod
    def read(self, n=-1):
        """Read n characters from the buffer"""

    @abstractmethod
    def write(self, s):
        """Write into the buffer"""

    @abstractmethod
    def seek(self, pos, mode=0):
        """Seek to a specific point in a file"""

    @abstractmethod
    def readline(self, length=None):
        """Returns the next available line"""

    @abstractmethod
    def readlines(self, sizehint=0):
        """Returns a list of all lines from the current position forward"""

    def xǁSpooledIOBaseǁwritelines__mutmut_orig(self, lines):
        """
        Write lines to the file from an interable.

        NOTE: writelines() does NOT add line separators.
        """
        self._checkClosed()
        for line in lines:
            self.write(line)

    def xǁSpooledIOBaseǁwritelines__mutmut_1(self, lines):
        """
        Write lines to the file from an interable.

        NOTE: writelines() does NOT add line separators.
        """
        self._checkClosed()
        for line in lines:
            self.write(None)
    
    xǁSpooledIOBaseǁwritelines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁwritelines__mutmut_1': xǁSpooledIOBaseǁwritelines__mutmut_1
    }
    
    def writelines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁwritelines__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁwritelines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    writelines.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁwritelines__mutmut_orig)
    xǁSpooledIOBaseǁwritelines__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁwritelines'

    @abstractmethod
    def rollover(self):
        """Roll file-like-object over into a real temporary file"""

    @abstractmethod
    def tell(self):
        """Return the current position"""

    @abstractproperty
    def buffer(self):
        """Should return a flo instance"""

    @abstractproperty
    def _rolled(self):
        """Returns whether the file has been rolled to a real file or not"""

    @abstractproperty
    def len(self):
        """Returns the length of the data"""

    def _get_softspace(self):
        return self.buffer.softspace

    def xǁSpooledIOBaseǁ_set_softspace__mutmut_orig(self, val):
        self.buffer.softspace = val

    def xǁSpooledIOBaseǁ_set_softspace__mutmut_1(self, val):
        self.buffer.softspace = None
    
    xǁSpooledIOBaseǁ_set_softspace__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ_set_softspace__mutmut_1': xǁSpooledIOBaseǁ_set_softspace__mutmut_1
    }
    
    def _set_softspace(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ_set_softspace__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ_set_softspace__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_softspace.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ_set_softspace__mutmut_orig)
    xǁSpooledIOBaseǁ_set_softspace__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ_set_softspace'

    softspace = property(_get_softspace, _set_softspace)

    @property
    def _file(self):
        return self.buffer

    def close(self):
        return self.buffer.close()

    def flush(self):
        self._checkClosed()
        return self.buffer.flush()

    def isatty(self):
        self._checkClosed()
        return self.buffer.isatty()

    @property
    def closed(self):
        return self.buffer.closed

    @property
    def pos(self):
        return self.tell()

    @property
    def buf(self):
        return self.getvalue()

    def fileno(self):
        self.rollover()
        return self.buffer.fileno()

    def xǁSpooledIOBaseǁtruncate__mutmut_orig(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_1(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is not None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_2(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size <= 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_3(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 1:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_4(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(None, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_5(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, None)

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_6(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError("Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_7(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, )

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_8(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "XXNegative size not allowedXX")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_9(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_10(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "NEGATIVE SIZE NOT ALLOWED")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_11(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = None
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_12(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(None)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_13(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos <= size:
            self.seek(pos)

    def xǁSpooledIOBaseǁtruncate__mutmut_14(self, size=None):
        """
        Truncate the contents of the buffer.

        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        self._checkClosed()
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise OSError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(None)
    
    xǁSpooledIOBaseǁtruncate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁtruncate__mutmut_1': xǁSpooledIOBaseǁtruncate__mutmut_1, 
        'xǁSpooledIOBaseǁtruncate__mutmut_2': xǁSpooledIOBaseǁtruncate__mutmut_2, 
        'xǁSpooledIOBaseǁtruncate__mutmut_3': xǁSpooledIOBaseǁtruncate__mutmut_3, 
        'xǁSpooledIOBaseǁtruncate__mutmut_4': xǁSpooledIOBaseǁtruncate__mutmut_4, 
        'xǁSpooledIOBaseǁtruncate__mutmut_5': xǁSpooledIOBaseǁtruncate__mutmut_5, 
        'xǁSpooledIOBaseǁtruncate__mutmut_6': xǁSpooledIOBaseǁtruncate__mutmut_6, 
        'xǁSpooledIOBaseǁtruncate__mutmut_7': xǁSpooledIOBaseǁtruncate__mutmut_7, 
        'xǁSpooledIOBaseǁtruncate__mutmut_8': xǁSpooledIOBaseǁtruncate__mutmut_8, 
        'xǁSpooledIOBaseǁtruncate__mutmut_9': xǁSpooledIOBaseǁtruncate__mutmut_9, 
        'xǁSpooledIOBaseǁtruncate__mutmut_10': xǁSpooledIOBaseǁtruncate__mutmut_10, 
        'xǁSpooledIOBaseǁtruncate__mutmut_11': xǁSpooledIOBaseǁtruncate__mutmut_11, 
        'xǁSpooledIOBaseǁtruncate__mutmut_12': xǁSpooledIOBaseǁtruncate__mutmut_12, 
        'xǁSpooledIOBaseǁtruncate__mutmut_13': xǁSpooledIOBaseǁtruncate__mutmut_13, 
        'xǁSpooledIOBaseǁtruncate__mutmut_14': xǁSpooledIOBaseǁtruncate__mutmut_14
    }
    
    def truncate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁtruncate__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁtruncate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    truncate.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁtruncate__mutmut_orig)
    xǁSpooledIOBaseǁtruncate__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁtruncate'

    def xǁSpooledIOBaseǁgetvalue__mutmut_orig(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = self.tell()
        self.seek(0)
        val = self.read()
        self.seek(pos)
        return val

    def xǁSpooledIOBaseǁgetvalue__mutmut_1(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = None
        self.seek(0)
        val = self.read()
        self.seek(pos)
        return val

    def xǁSpooledIOBaseǁgetvalue__mutmut_2(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = self.tell()
        self.seek(None)
        val = self.read()
        self.seek(pos)
        return val

    def xǁSpooledIOBaseǁgetvalue__mutmut_3(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = self.tell()
        self.seek(1)
        val = self.read()
        self.seek(pos)
        return val

    def xǁSpooledIOBaseǁgetvalue__mutmut_4(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = self.tell()
        self.seek(0)
        val = None
        self.seek(pos)
        return val

    def xǁSpooledIOBaseǁgetvalue__mutmut_5(self):
        """Return the entire files contents."""
        self._checkClosed()
        pos = self.tell()
        self.seek(0)
        val = self.read()
        self.seek(None)
        return val
    
    xǁSpooledIOBaseǁgetvalue__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁgetvalue__mutmut_1': xǁSpooledIOBaseǁgetvalue__mutmut_1, 
        'xǁSpooledIOBaseǁgetvalue__mutmut_2': xǁSpooledIOBaseǁgetvalue__mutmut_2, 
        'xǁSpooledIOBaseǁgetvalue__mutmut_3': xǁSpooledIOBaseǁgetvalue__mutmut_3, 
        'xǁSpooledIOBaseǁgetvalue__mutmut_4': xǁSpooledIOBaseǁgetvalue__mutmut_4, 
        'xǁSpooledIOBaseǁgetvalue__mutmut_5': xǁSpooledIOBaseǁgetvalue__mutmut_5
    }
    
    def getvalue(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁgetvalue__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁgetvalue__mutmut_mutants"), args, kwargs, self)
        return result 
    
    getvalue.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁgetvalue__mutmut_orig)
    xǁSpooledIOBaseǁgetvalue__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁgetvalue'

    def xǁSpooledIOBaseǁseekable__mutmut_orig(self):
        return True

    def xǁSpooledIOBaseǁseekable__mutmut_1(self):
        return False
    
    xǁSpooledIOBaseǁseekable__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁseekable__mutmut_1': xǁSpooledIOBaseǁseekable__mutmut_1
    }
    
    def seekable(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁseekable__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁseekable__mutmut_mutants"), args, kwargs, self)
        return result 
    
    seekable.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁseekable__mutmut_orig)
    xǁSpooledIOBaseǁseekable__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁseekable'

    def xǁSpooledIOBaseǁreadable__mutmut_orig(self):
        return True

    def xǁSpooledIOBaseǁreadable__mutmut_1(self):
        return False
    
    xǁSpooledIOBaseǁreadable__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁreadable__mutmut_1': xǁSpooledIOBaseǁreadable__mutmut_1
    }
    
    def readable(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁreadable__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁreadable__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readable.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁreadable__mutmut_orig)
    xǁSpooledIOBaseǁreadable__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁreadable'

    def xǁSpooledIOBaseǁwritable__mutmut_orig(self):
        return True

    def xǁSpooledIOBaseǁwritable__mutmut_1(self):
        return False
    
    xǁSpooledIOBaseǁwritable__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁwritable__mutmut_1': xǁSpooledIOBaseǁwritable__mutmut_1
    }
    
    def writable(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁwritable__mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁwritable__mutmut_mutants"), args, kwargs, self)
        return result 
    
    writable.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁwritable__mutmut_orig)
    xǁSpooledIOBaseǁwritable__mutmut_orig.__name__ = 'xǁSpooledIOBaseǁwritable'

    def xǁSpooledIOBaseǁ__next____mutmut_orig(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_1(self):
        self._checkClosed()
        line = None
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_2(self):
        self._checkClosed()
        line = self.readline()
        if line:
            pos = self.buffer.tell()
            self.buffer.seek(0, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_3(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = None
            self.buffer.seek(0, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_4(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(None, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_5(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, None)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_6(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_7(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, )
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_8(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(1, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_9(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, os.SEEK_END)
            if pos != self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(pos)
        return line

    def xǁSpooledIOBaseǁ__next____mutmut_10(self):
        self._checkClosed()
        line = self.readline()
        if not line:
            pos = self.buffer.tell()
            self.buffer.seek(0, os.SEEK_END)
            if pos == self.buffer.tell():
                raise StopIteration
            else:
                self.buffer.seek(None)
        return line
    
    xǁSpooledIOBaseǁ__next____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ__next____mutmut_1': xǁSpooledIOBaseǁ__next____mutmut_1, 
        'xǁSpooledIOBaseǁ__next____mutmut_2': xǁSpooledIOBaseǁ__next____mutmut_2, 
        'xǁSpooledIOBaseǁ__next____mutmut_3': xǁSpooledIOBaseǁ__next____mutmut_3, 
        'xǁSpooledIOBaseǁ__next____mutmut_4': xǁSpooledIOBaseǁ__next____mutmut_4, 
        'xǁSpooledIOBaseǁ__next____mutmut_5': xǁSpooledIOBaseǁ__next____mutmut_5, 
        'xǁSpooledIOBaseǁ__next____mutmut_6': xǁSpooledIOBaseǁ__next____mutmut_6, 
        'xǁSpooledIOBaseǁ__next____mutmut_7': xǁSpooledIOBaseǁ__next____mutmut_7, 
        'xǁSpooledIOBaseǁ__next____mutmut_8': xǁSpooledIOBaseǁ__next____mutmut_8, 
        'xǁSpooledIOBaseǁ__next____mutmut_9': xǁSpooledIOBaseǁ__next____mutmut_9, 
        'xǁSpooledIOBaseǁ__next____mutmut_10': xǁSpooledIOBaseǁ__next____mutmut_10
    }
    
    def __next__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ__next____mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ__next____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __next__.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ__next____mutmut_orig)
    xǁSpooledIOBaseǁ__next____mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ__next__'

    next = __next__

    def __len__(self):
        return self.len

    def __iter__(self):
        self._checkClosed()
        return self

    def __enter__(self):
        self._checkClosed()
        return self

    def __exit__(self, *args):
        self._file.close()

    def xǁSpooledIOBaseǁ__eq____mutmut_orig(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_1(self, other):
        if isinstance(other, self.__class__):
            self_pos = None
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_2(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = None
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_3(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(None)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_4(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(1)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_5(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(None)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_6(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(1)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_7(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = None
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_8(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = False
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_9(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(None, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_10(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, None):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_11(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_12(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, ):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_13(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line == other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_14(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = None
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_15(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = True
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_16(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        return
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_17(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(None)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_18(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(None)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_19(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(None)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_20(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(None)
                except Exception:
                    pass
                raise
            else:
                return eq
        return False

    def xǁSpooledIOBaseǁ__eq____mutmut_21(self, other):
        if isinstance(other, self.__class__):
            self_pos = self.tell()
            other_pos = other.tell()
            try:
                self.seek(0)
                other.seek(0)
                eq = True
                for self_line, other_line in zip_longest(self, other):
                    if self_line != other_line:
                        eq = False
                        break
                self.seek(self_pos)
                other.seek(other_pos)
            except Exception:
                # Attempt to return files to original position if there were any errors
                try:
                    self.seek(self_pos)
                except Exception:
                    pass
                try:
                    other.seek(other_pos)
                except Exception:
                    pass
                raise
            else:
                return eq
        return True
    
    xǁSpooledIOBaseǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ__eq____mutmut_1': xǁSpooledIOBaseǁ__eq____mutmut_1, 
        'xǁSpooledIOBaseǁ__eq____mutmut_2': xǁSpooledIOBaseǁ__eq____mutmut_2, 
        'xǁSpooledIOBaseǁ__eq____mutmut_3': xǁSpooledIOBaseǁ__eq____mutmut_3, 
        'xǁSpooledIOBaseǁ__eq____mutmut_4': xǁSpooledIOBaseǁ__eq____mutmut_4, 
        'xǁSpooledIOBaseǁ__eq____mutmut_5': xǁSpooledIOBaseǁ__eq____mutmut_5, 
        'xǁSpooledIOBaseǁ__eq____mutmut_6': xǁSpooledIOBaseǁ__eq____mutmut_6, 
        'xǁSpooledIOBaseǁ__eq____mutmut_7': xǁSpooledIOBaseǁ__eq____mutmut_7, 
        'xǁSpooledIOBaseǁ__eq____mutmut_8': xǁSpooledIOBaseǁ__eq____mutmut_8, 
        'xǁSpooledIOBaseǁ__eq____mutmut_9': xǁSpooledIOBaseǁ__eq____mutmut_9, 
        'xǁSpooledIOBaseǁ__eq____mutmut_10': xǁSpooledIOBaseǁ__eq____mutmut_10, 
        'xǁSpooledIOBaseǁ__eq____mutmut_11': xǁSpooledIOBaseǁ__eq____mutmut_11, 
        'xǁSpooledIOBaseǁ__eq____mutmut_12': xǁSpooledIOBaseǁ__eq____mutmut_12, 
        'xǁSpooledIOBaseǁ__eq____mutmut_13': xǁSpooledIOBaseǁ__eq____mutmut_13, 
        'xǁSpooledIOBaseǁ__eq____mutmut_14': xǁSpooledIOBaseǁ__eq____mutmut_14, 
        'xǁSpooledIOBaseǁ__eq____mutmut_15': xǁSpooledIOBaseǁ__eq____mutmut_15, 
        'xǁSpooledIOBaseǁ__eq____mutmut_16': xǁSpooledIOBaseǁ__eq____mutmut_16, 
        'xǁSpooledIOBaseǁ__eq____mutmut_17': xǁSpooledIOBaseǁ__eq____mutmut_17, 
        'xǁSpooledIOBaseǁ__eq____mutmut_18': xǁSpooledIOBaseǁ__eq____mutmut_18, 
        'xǁSpooledIOBaseǁ__eq____mutmut_19': xǁSpooledIOBaseǁ__eq____mutmut_19, 
        'xǁSpooledIOBaseǁ__eq____mutmut_20': xǁSpooledIOBaseǁ__eq____mutmut_20, 
        'xǁSpooledIOBaseǁ__eq____mutmut_21': xǁSpooledIOBaseǁ__eq____mutmut_21
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ__eq____mutmut_orig)
    xǁSpooledIOBaseǁ__eq____mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ__eq__'

    def xǁSpooledIOBaseǁ__ne____mutmut_orig(self, other):
        return not self.__eq__(other)

    def xǁSpooledIOBaseǁ__ne____mutmut_1(self, other):
        return self.__eq__(other)

    def xǁSpooledIOBaseǁ__ne____mutmut_2(self, other):
        return not self.__eq__(None)
    
    xǁSpooledIOBaseǁ__ne____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ__ne____mutmut_1': xǁSpooledIOBaseǁ__ne____mutmut_1, 
        'xǁSpooledIOBaseǁ__ne____mutmut_2': xǁSpooledIOBaseǁ__ne____mutmut_2
    }
    
    def __ne__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ__ne____mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ__ne____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ne__.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ__ne____mutmut_orig)
    xǁSpooledIOBaseǁ__ne____mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ__ne__'

    def xǁSpooledIOBaseǁ__bool____mutmut_orig(self):
        return True

    def xǁSpooledIOBaseǁ__bool____mutmut_1(self):
        return False
    
    xǁSpooledIOBaseǁ__bool____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledIOBaseǁ__bool____mutmut_1': xǁSpooledIOBaseǁ__bool____mutmut_1
    }
    
    def __bool__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledIOBaseǁ__bool____mutmut_orig"), object.__getattribute__(self, "xǁSpooledIOBaseǁ__bool____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __bool__.__signature__ = _mutmut_signature(xǁSpooledIOBaseǁ__bool____mutmut_orig)
    xǁSpooledIOBaseǁ__bool____mutmut_orig.__name__ = 'xǁSpooledIOBaseǁ__bool__'

    def __del__(self):
        """Can fail when called at program exit so suppress traceback."""
        try:
            self.close()
        except Exception:
            pass


class SpooledBytesIO(SpooledIOBase):
    """
    SpooledBytesIO is a spooled file-like-object that only accepts bytes. On
    Python 2.x this means the 'str' type; on Python 3.x this means the 'bytes'
    type. Bytes are written in and retrieved exactly as given, but it will
    raise TypeErrors if something other than bytes are written.

    Example::

        >>> from boltons import ioutils
        >>> with ioutils.SpooledBytesIO() as f:
        ...     f.write(b"Happy IO")
        ...     _ = f.seek(0)
        ...     isinstance(f.getvalue(), bytes)
        True
    """

    def xǁSpooledBytesIOǁread__mutmut_orig(self, n=-1):
        self._checkClosed()
        return self.buffer.read(n)

    def xǁSpooledBytesIOǁread__mutmut_1(self, n=-1):
        self._checkClosed()
        return self.buffer.read(None)
    
    xǁSpooledBytesIOǁread__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁread__mutmut_1': xǁSpooledBytesIOǁread__mutmut_1
    }
    
    def read(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁread__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁread__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁread__mutmut_orig)
    xǁSpooledBytesIOǁread__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁread'

    def xǁSpooledBytesIOǁwrite__mutmut_orig(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_1(self, s):
        self._checkClosed()
        if isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_2(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError(None)

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_3(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                None
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_4(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("XXbytes expected, got {}XX".format(
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_5(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("BYTES EXPECTED, GOT {}".format(
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_6(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(None).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_7(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(s).__name__
            ))

        if self.tell() - len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_8(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(s).__name__
            ))

        if self.tell() + len(s) > self._max_size:
            self.rollover()
        self.buffer.write(s)

    def xǁSpooledBytesIOǁwrite__mutmut_9(self, s):
        self._checkClosed()
        if not isinstance(s, bytes):
            raise TypeError("bytes expected, got {}".format(
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(None)
    
    xǁSpooledBytesIOǁwrite__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁwrite__mutmut_1': xǁSpooledBytesIOǁwrite__mutmut_1, 
        'xǁSpooledBytesIOǁwrite__mutmut_2': xǁSpooledBytesIOǁwrite__mutmut_2, 
        'xǁSpooledBytesIOǁwrite__mutmut_3': xǁSpooledBytesIOǁwrite__mutmut_3, 
        'xǁSpooledBytesIOǁwrite__mutmut_4': xǁSpooledBytesIOǁwrite__mutmut_4, 
        'xǁSpooledBytesIOǁwrite__mutmut_5': xǁSpooledBytesIOǁwrite__mutmut_5, 
        'xǁSpooledBytesIOǁwrite__mutmut_6': xǁSpooledBytesIOǁwrite__mutmut_6, 
        'xǁSpooledBytesIOǁwrite__mutmut_7': xǁSpooledBytesIOǁwrite__mutmut_7, 
        'xǁSpooledBytesIOǁwrite__mutmut_8': xǁSpooledBytesIOǁwrite__mutmut_8, 
        'xǁSpooledBytesIOǁwrite__mutmut_9': xǁSpooledBytesIOǁwrite__mutmut_9
    }
    
    def write(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁwrite__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁwrite__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁwrite__mutmut_orig)
    xǁSpooledBytesIOǁwrite__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁwrite'

    def xǁSpooledBytesIOǁseek__mutmut_orig(self, pos, mode=0):
        self._checkClosed()
        return self.buffer.seek(pos, mode)

    def xǁSpooledBytesIOǁseek__mutmut_1(self, pos, mode=1):
        self._checkClosed()
        return self.buffer.seek(pos, mode)

    def xǁSpooledBytesIOǁseek__mutmut_2(self, pos, mode=0):
        self._checkClosed()
        return self.buffer.seek(None, mode)

    def xǁSpooledBytesIOǁseek__mutmut_3(self, pos, mode=0):
        self._checkClosed()
        return self.buffer.seek(pos, None)

    def xǁSpooledBytesIOǁseek__mutmut_4(self, pos, mode=0):
        self._checkClosed()
        return self.buffer.seek(mode)

    def xǁSpooledBytesIOǁseek__mutmut_5(self, pos, mode=0):
        self._checkClosed()
        return self.buffer.seek(pos, )
    
    xǁSpooledBytesIOǁseek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁseek__mutmut_1': xǁSpooledBytesIOǁseek__mutmut_1, 
        'xǁSpooledBytesIOǁseek__mutmut_2': xǁSpooledBytesIOǁseek__mutmut_2, 
        'xǁSpooledBytesIOǁseek__mutmut_3': xǁSpooledBytesIOǁseek__mutmut_3, 
        'xǁSpooledBytesIOǁseek__mutmut_4': xǁSpooledBytesIOǁseek__mutmut_4, 
        'xǁSpooledBytesIOǁseek__mutmut_5': xǁSpooledBytesIOǁseek__mutmut_5
    }
    
    def seek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁseek__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁseek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    seek.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁseek__mutmut_orig)
    xǁSpooledBytesIOǁseek__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁseek'

    def xǁSpooledBytesIOǁreadline__mutmut_orig(self, length=None):
        self._checkClosed()
        if length:
            return self.buffer.readline(length)
        else:
            return self.buffer.readline()

    def xǁSpooledBytesIOǁreadline__mutmut_1(self, length=None):
        self._checkClosed()
        if length:
            return self.buffer.readline(None)
        else:
            return self.buffer.readline()
    
    xǁSpooledBytesIOǁreadline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁreadline__mutmut_1': xǁSpooledBytesIOǁreadline__mutmut_1
    }
    
    def readline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁreadline__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁreadline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readline.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁreadline__mutmut_orig)
    xǁSpooledBytesIOǁreadline__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁreadline'

    def xǁSpooledBytesIOǁreadlines__mutmut_orig(self, sizehint=0):
        return self.buffer.readlines(sizehint)

    def xǁSpooledBytesIOǁreadlines__mutmut_1(self, sizehint=1):
        return self.buffer.readlines(sizehint)

    def xǁSpooledBytesIOǁreadlines__mutmut_2(self, sizehint=0):
        return self.buffer.readlines(None)
    
    xǁSpooledBytesIOǁreadlines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁreadlines__mutmut_1': xǁSpooledBytesIOǁreadlines__mutmut_1, 
        'xǁSpooledBytesIOǁreadlines__mutmut_2': xǁSpooledBytesIOǁreadlines__mutmut_2
    }
    
    def readlines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁreadlines__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁreadlines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readlines.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁreadlines__mutmut_orig)
    xǁSpooledBytesIOǁreadlines__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁreadlines'

    def xǁSpooledBytesIOǁrollover__mutmut_orig(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_1(self):
        """Roll the StringIO over to a TempFile"""
        if self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_2(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = None
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_3(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=None)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_4(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = None
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_5(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = self.buffer.tell()
            tmp.write(None)
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_6(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(None)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledBytesIOǁrollover__mutmut_7(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile(dir=self._dir)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = None
    
    xǁSpooledBytesIOǁrollover__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledBytesIOǁrollover__mutmut_1': xǁSpooledBytesIOǁrollover__mutmut_1, 
        'xǁSpooledBytesIOǁrollover__mutmut_2': xǁSpooledBytesIOǁrollover__mutmut_2, 
        'xǁSpooledBytesIOǁrollover__mutmut_3': xǁSpooledBytesIOǁrollover__mutmut_3, 
        'xǁSpooledBytesIOǁrollover__mutmut_4': xǁSpooledBytesIOǁrollover__mutmut_4, 
        'xǁSpooledBytesIOǁrollover__mutmut_5': xǁSpooledBytesIOǁrollover__mutmut_5, 
        'xǁSpooledBytesIOǁrollover__mutmut_6': xǁSpooledBytesIOǁrollover__mutmut_6, 
        'xǁSpooledBytesIOǁrollover__mutmut_7': xǁSpooledBytesIOǁrollover__mutmut_7
    }
    
    def rollover(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledBytesIOǁrollover__mutmut_orig"), object.__getattribute__(self, "xǁSpooledBytesIOǁrollover__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rollover.__signature__ = _mutmut_signature(xǁSpooledBytesIOǁrollover__mutmut_orig)
    xǁSpooledBytesIOǁrollover__mutmut_orig.__name__ = 'xǁSpooledBytesIOǁrollover'

    @property
    def _rolled(self):
        return not isinstance(self.buffer, BytesIO)

    @property
    def buffer(self):
        try:
            return self._buffer
        except AttributeError:
            self._buffer = BytesIO()
        return self._buffer

    @property
    def len(self):
        """Determine the length of the file"""
        pos = self.tell()
        if self._rolled:
            self.seek(0)
            val = os.fstat(self.fileno()).st_size
        else:
            self.seek(0, os.SEEK_END)
            val = self.tell()
        self.seek(pos)
        return val

    def tell(self):
        self._checkClosed()
        return self.buffer.tell()


class SpooledStringIO(SpooledIOBase):
    """
    SpooledStringIO is a spooled file-like-object that only accepts unicode
    values. On Python 2.x this means the 'unicode' type and on Python 3.x this
    means the 'str' type. Values are accepted as unicode and then coerced into
    utf-8 encoded bytes for storage. On retrieval, the values are returned as
    unicode.

    Example::

        >>> from boltons import ioutils
        >>> with ioutils.SpooledStringIO() as f:
        ...     f.write(u"\u2014 Hey, an emdash!")
        ...     _ = f.seek(0)
        ...     isinstance(f.read(), str)
        True

    """
    def xǁSpooledStringIOǁ__init____mutmut_orig(self, *args, **kwargs):
        self._tell = 0
        super().__init__(*args, **kwargs)
    def xǁSpooledStringIOǁ__init____mutmut_1(self, *args, **kwargs):
        self._tell = None
        super().__init__(*args, **kwargs)
    def xǁSpooledStringIOǁ__init____mutmut_2(self, *args, **kwargs):
        self._tell = 1
        super().__init__(*args, **kwargs)
    def xǁSpooledStringIOǁ__init____mutmut_3(self, *args, **kwargs):
        self._tell = 0
        super().__init__(**kwargs)
    def xǁSpooledStringIOǁ__init____mutmut_4(self, *args, **kwargs):
        self._tell = 0
        super().__init__(*args, )
    
    xǁSpooledStringIOǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁ__init____mutmut_1': xǁSpooledStringIOǁ__init____mutmut_1, 
        'xǁSpooledStringIOǁ__init____mutmut_2': xǁSpooledStringIOǁ__init____mutmut_2, 
        'xǁSpooledStringIOǁ__init____mutmut_3': xǁSpooledStringIOǁ__init____mutmut_3, 
        'xǁSpooledStringIOǁ__init____mutmut_4': xǁSpooledStringIOǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSpooledStringIOǁ__init____mutmut_orig)
    xǁSpooledStringIOǁ__init____mutmut_orig.__name__ = 'xǁSpooledStringIOǁ__init__'

    def xǁSpooledStringIOǁread__mutmut_orig(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n, n)
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_1(self, n=-1):
        self._checkClosed()
        ret = None
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_2(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(None, n)
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_3(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n, None)
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_4(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n)
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_5(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n, )
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁread__mutmut_6(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n, n)
        self._tell = None
        return ret

    def xǁSpooledStringIOǁread__mutmut_7(self, n=-1):
        self._checkClosed()
        ret = self.buffer.reader.read(n, n)
        self._tell = self.tell() - len(ret)
        return ret
    
    xǁSpooledStringIOǁread__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁread__mutmut_1': xǁSpooledStringIOǁread__mutmut_1, 
        'xǁSpooledStringIOǁread__mutmut_2': xǁSpooledStringIOǁread__mutmut_2, 
        'xǁSpooledStringIOǁread__mutmut_3': xǁSpooledStringIOǁread__mutmut_3, 
        'xǁSpooledStringIOǁread__mutmut_4': xǁSpooledStringIOǁread__mutmut_4, 
        'xǁSpooledStringIOǁread__mutmut_5': xǁSpooledStringIOǁread__mutmut_5, 
        'xǁSpooledStringIOǁread__mutmut_6': xǁSpooledStringIOǁread__mutmut_6, 
        'xǁSpooledStringIOǁread__mutmut_7': xǁSpooledStringIOǁread__mutmut_7
    }
    
    def read(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁread__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁread__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read.__signature__ = _mutmut_signature(xǁSpooledStringIOǁread__mutmut_orig)
    xǁSpooledStringIOǁread__mutmut_orig.__name__ = 'xǁSpooledStringIOǁread'

    def xǁSpooledStringIOǁwrite__mutmut_orig(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_1(self, s):
        self._checkClosed()
        if isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_2(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError(None)
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_3(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                None
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_4(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("XXstr expected, got {}XX".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_5(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("STR EXPECTED, GOT {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_6(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(None).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_7(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = None
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_8(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() - len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_9(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) > self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_10(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(None)
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_11(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode(None))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_12(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('XXutf-8XX'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_13(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('UTF-8'))
        self._tell = current_pos + len(s)

    def xǁSpooledStringIOǁwrite__mutmut_14(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = None

    def xǁSpooledStringIOǁwrite__mutmut_15(self, s):
        self._checkClosed()
        if not isinstance(s, str):
            raise TypeError("str expected, got {}".format(
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos - len(s)
    
    xǁSpooledStringIOǁwrite__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁwrite__mutmut_1': xǁSpooledStringIOǁwrite__mutmut_1, 
        'xǁSpooledStringIOǁwrite__mutmut_2': xǁSpooledStringIOǁwrite__mutmut_2, 
        'xǁSpooledStringIOǁwrite__mutmut_3': xǁSpooledStringIOǁwrite__mutmut_3, 
        'xǁSpooledStringIOǁwrite__mutmut_4': xǁSpooledStringIOǁwrite__mutmut_4, 
        'xǁSpooledStringIOǁwrite__mutmut_5': xǁSpooledStringIOǁwrite__mutmut_5, 
        'xǁSpooledStringIOǁwrite__mutmut_6': xǁSpooledStringIOǁwrite__mutmut_6, 
        'xǁSpooledStringIOǁwrite__mutmut_7': xǁSpooledStringIOǁwrite__mutmut_7, 
        'xǁSpooledStringIOǁwrite__mutmut_8': xǁSpooledStringIOǁwrite__mutmut_8, 
        'xǁSpooledStringIOǁwrite__mutmut_9': xǁSpooledStringIOǁwrite__mutmut_9, 
        'xǁSpooledStringIOǁwrite__mutmut_10': xǁSpooledStringIOǁwrite__mutmut_10, 
        'xǁSpooledStringIOǁwrite__mutmut_11': xǁSpooledStringIOǁwrite__mutmut_11, 
        'xǁSpooledStringIOǁwrite__mutmut_12': xǁSpooledStringIOǁwrite__mutmut_12, 
        'xǁSpooledStringIOǁwrite__mutmut_13': xǁSpooledStringIOǁwrite__mutmut_13, 
        'xǁSpooledStringIOǁwrite__mutmut_14': xǁSpooledStringIOǁwrite__mutmut_14, 
        'xǁSpooledStringIOǁwrite__mutmut_15': xǁSpooledStringIOǁwrite__mutmut_15
    }
    
    def write(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁwrite__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁwrite__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write.__signature__ = _mutmut_signature(xǁSpooledStringIOǁwrite__mutmut_orig)
    xǁSpooledStringIOǁwrite__mutmut_orig.__name__ = 'xǁSpooledStringIOǁwrite'

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_orig(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_1(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = None
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_2(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position - n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_3(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while False:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_4(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position != dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_5(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                return

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_6(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position - READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_7(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE >= dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_8(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(None)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_9(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest + current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_10(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                return
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_11(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = None

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_12(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(None)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_13(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position = READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_14(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position -= READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_15(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if ret:
                break

        return dest

    def xǁSpooledStringIOǁ_traverse_codepoints__mutmut_16(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                return

        return dest
    
    xǁSpooledStringIOǁ_traverse_codepoints__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_1': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_1, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_2': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_2, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_3': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_3, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_4': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_4, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_5': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_5, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_6': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_6, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_7': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_7, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_8': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_8, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_9': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_9, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_10': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_10, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_11': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_11, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_12': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_12, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_13': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_13, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_14': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_14, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_15': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_15, 
        'xǁSpooledStringIOǁ_traverse_codepoints__mutmut_16': xǁSpooledStringIOǁ_traverse_codepoints__mutmut_16
    }
    
    def _traverse_codepoints(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁ_traverse_codepoints__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁ_traverse_codepoints__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _traverse_codepoints.__signature__ = _mutmut_signature(xǁSpooledStringIOǁ_traverse_codepoints__mutmut_orig)
    xǁSpooledStringIOǁ_traverse_codepoints__mutmut_orig.__name__ = 'xǁSpooledStringIOǁ_traverse_codepoints'

    def xǁSpooledStringIOǁseek__mutmut_orig(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_1(self, pos, mode=1):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_2(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode != os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_3(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(None)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_4(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(1)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_5(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(None, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_6(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, None)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_7(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_8(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, )
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_9(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(1, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_10(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = None
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_11(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode != os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_12(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = None
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_13(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(None, pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_14(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), None)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_15(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_16(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), )
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_17(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = None
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_18(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos - pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_19(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode != os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_20(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(None)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_21(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(1)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_22(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = None
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_23(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len + pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_24(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(None, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_25(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, None)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_26(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_27(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, )
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_28(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(1, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_29(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = None
        else:
            raise ValueError(
                f"Invalid whence ({mode}, should be 0, 1, or 2)"
            )
        return self.tell()

    def xǁSpooledStringIOǁseek__mutmut_30(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        self._checkClosed()
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                None
            )
        return self.tell()
    
    xǁSpooledStringIOǁseek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁseek__mutmut_1': xǁSpooledStringIOǁseek__mutmut_1, 
        'xǁSpooledStringIOǁseek__mutmut_2': xǁSpooledStringIOǁseek__mutmut_2, 
        'xǁSpooledStringIOǁseek__mutmut_3': xǁSpooledStringIOǁseek__mutmut_3, 
        'xǁSpooledStringIOǁseek__mutmut_4': xǁSpooledStringIOǁseek__mutmut_4, 
        'xǁSpooledStringIOǁseek__mutmut_5': xǁSpooledStringIOǁseek__mutmut_5, 
        'xǁSpooledStringIOǁseek__mutmut_6': xǁSpooledStringIOǁseek__mutmut_6, 
        'xǁSpooledStringIOǁseek__mutmut_7': xǁSpooledStringIOǁseek__mutmut_7, 
        'xǁSpooledStringIOǁseek__mutmut_8': xǁSpooledStringIOǁseek__mutmut_8, 
        'xǁSpooledStringIOǁseek__mutmut_9': xǁSpooledStringIOǁseek__mutmut_9, 
        'xǁSpooledStringIOǁseek__mutmut_10': xǁSpooledStringIOǁseek__mutmut_10, 
        'xǁSpooledStringIOǁseek__mutmut_11': xǁSpooledStringIOǁseek__mutmut_11, 
        'xǁSpooledStringIOǁseek__mutmut_12': xǁSpooledStringIOǁseek__mutmut_12, 
        'xǁSpooledStringIOǁseek__mutmut_13': xǁSpooledStringIOǁseek__mutmut_13, 
        'xǁSpooledStringIOǁseek__mutmut_14': xǁSpooledStringIOǁseek__mutmut_14, 
        'xǁSpooledStringIOǁseek__mutmut_15': xǁSpooledStringIOǁseek__mutmut_15, 
        'xǁSpooledStringIOǁseek__mutmut_16': xǁSpooledStringIOǁseek__mutmut_16, 
        'xǁSpooledStringIOǁseek__mutmut_17': xǁSpooledStringIOǁseek__mutmut_17, 
        'xǁSpooledStringIOǁseek__mutmut_18': xǁSpooledStringIOǁseek__mutmut_18, 
        'xǁSpooledStringIOǁseek__mutmut_19': xǁSpooledStringIOǁseek__mutmut_19, 
        'xǁSpooledStringIOǁseek__mutmut_20': xǁSpooledStringIOǁseek__mutmut_20, 
        'xǁSpooledStringIOǁseek__mutmut_21': xǁSpooledStringIOǁseek__mutmut_21, 
        'xǁSpooledStringIOǁseek__mutmut_22': xǁSpooledStringIOǁseek__mutmut_22, 
        'xǁSpooledStringIOǁseek__mutmut_23': xǁSpooledStringIOǁseek__mutmut_23, 
        'xǁSpooledStringIOǁseek__mutmut_24': xǁSpooledStringIOǁseek__mutmut_24, 
        'xǁSpooledStringIOǁseek__mutmut_25': xǁSpooledStringIOǁseek__mutmut_25, 
        'xǁSpooledStringIOǁseek__mutmut_26': xǁSpooledStringIOǁseek__mutmut_26, 
        'xǁSpooledStringIOǁseek__mutmut_27': xǁSpooledStringIOǁseek__mutmut_27, 
        'xǁSpooledStringIOǁseek__mutmut_28': xǁSpooledStringIOǁseek__mutmut_28, 
        'xǁSpooledStringIOǁseek__mutmut_29': xǁSpooledStringIOǁseek__mutmut_29, 
        'xǁSpooledStringIOǁseek__mutmut_30': xǁSpooledStringIOǁseek__mutmut_30
    }
    
    def seek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁseek__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁseek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    seek.__signature__ = _mutmut_signature(xǁSpooledStringIOǁseek__mutmut_orig)
    xǁSpooledStringIOǁseek__mutmut_orig.__name__ = 'xǁSpooledStringIOǁseek'

    def xǁSpooledStringIOǁreadline__mutmut_orig(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode('utf-8')
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_1(self, length=None):
        self._checkClosed()
        ret = None
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_2(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode(None)
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_3(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(None).decode('utf-8')
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_4(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode('XXutf-8XX')
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_5(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode('UTF-8')
        self._tell = self.tell() + len(ret)
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_6(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode('utf-8')
        self._tell = None
        return ret

    def xǁSpooledStringIOǁreadline__mutmut_7(self, length=None):
        self._checkClosed()
        ret = self.buffer.readline(length).decode('utf-8')
        self._tell = self.tell() - len(ret)
        return ret
    
    xǁSpooledStringIOǁreadline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁreadline__mutmut_1': xǁSpooledStringIOǁreadline__mutmut_1, 
        'xǁSpooledStringIOǁreadline__mutmut_2': xǁSpooledStringIOǁreadline__mutmut_2, 
        'xǁSpooledStringIOǁreadline__mutmut_3': xǁSpooledStringIOǁreadline__mutmut_3, 
        'xǁSpooledStringIOǁreadline__mutmut_4': xǁSpooledStringIOǁreadline__mutmut_4, 
        'xǁSpooledStringIOǁreadline__mutmut_5': xǁSpooledStringIOǁreadline__mutmut_5, 
        'xǁSpooledStringIOǁreadline__mutmut_6': xǁSpooledStringIOǁreadline__mutmut_6, 
        'xǁSpooledStringIOǁreadline__mutmut_7': xǁSpooledStringIOǁreadline__mutmut_7
    }
    
    def readline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁreadline__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁreadline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readline.__signature__ = _mutmut_signature(xǁSpooledStringIOǁreadline__mutmut_orig)
    xǁSpooledStringIOǁreadline__mutmut_orig.__name__ = 'xǁSpooledStringIOǁreadline'

    def xǁSpooledStringIOǁreadlines__mutmut_orig(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_1(self, sizehint=1):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_2(self, sizehint=0):
        ret = None
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_3(self, sizehint=0):
        ret = [x.decode(None) for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_4(self, sizehint=0):
        ret = [x.decode('XXutf-8XX') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_5(self, sizehint=0):
        ret = [x.decode('UTF-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_6(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(None)]
        self._tell = self.tell() + sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_7(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = None
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_8(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() - sum(len(x) for x in ret)
        return ret

    def xǁSpooledStringIOǁreadlines__mutmut_9(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum(None)
        return ret
    
    xǁSpooledStringIOǁreadlines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁreadlines__mutmut_1': xǁSpooledStringIOǁreadlines__mutmut_1, 
        'xǁSpooledStringIOǁreadlines__mutmut_2': xǁSpooledStringIOǁreadlines__mutmut_2, 
        'xǁSpooledStringIOǁreadlines__mutmut_3': xǁSpooledStringIOǁreadlines__mutmut_3, 
        'xǁSpooledStringIOǁreadlines__mutmut_4': xǁSpooledStringIOǁreadlines__mutmut_4, 
        'xǁSpooledStringIOǁreadlines__mutmut_5': xǁSpooledStringIOǁreadlines__mutmut_5, 
        'xǁSpooledStringIOǁreadlines__mutmut_6': xǁSpooledStringIOǁreadlines__mutmut_6, 
        'xǁSpooledStringIOǁreadlines__mutmut_7': xǁSpooledStringIOǁreadlines__mutmut_7, 
        'xǁSpooledStringIOǁreadlines__mutmut_8': xǁSpooledStringIOǁreadlines__mutmut_8, 
        'xǁSpooledStringIOǁreadlines__mutmut_9': xǁSpooledStringIOǁreadlines__mutmut_9
    }
    
    def readlines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁreadlines__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁreadlines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readlines.__signature__ = _mutmut_signature(xǁSpooledStringIOǁreadlines__mutmut_orig)
    xǁSpooledStringIOǁreadlines__mutmut_orig.__name__ = 'xǁSpooledStringIOǁreadlines'

    @property
    def buffer(self):
        try:
            return self._buffer
        except AttributeError:
            self._buffer = EncodedFile(BytesIO(), data_encoding='utf-8')
        return self._buffer

    @property
    def _rolled(self):
        return not isinstance(self.buffer.stream, BytesIO)

    def xǁSpooledStringIOǁrollover__mutmut_orig(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_1(self):
        """Roll the buffer over to a TempFile"""
        if self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_2(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = None
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_3(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(None,
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_4(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding=None)
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_5(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_6(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              )
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_7(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=None),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_8(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='XXutf-8XX')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_9(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='UTF-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_10(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = None
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_11(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(None)
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_12(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(None)
            self.buffer.close()
            self._buffer = tmp

    def xǁSpooledStringIOǁrollover__mutmut_13(self):
        """Roll the buffer over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(dir=self._dir),
                              data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = None
    
    xǁSpooledStringIOǁrollover__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSpooledStringIOǁrollover__mutmut_1': xǁSpooledStringIOǁrollover__mutmut_1, 
        'xǁSpooledStringIOǁrollover__mutmut_2': xǁSpooledStringIOǁrollover__mutmut_2, 
        'xǁSpooledStringIOǁrollover__mutmut_3': xǁSpooledStringIOǁrollover__mutmut_3, 
        'xǁSpooledStringIOǁrollover__mutmut_4': xǁSpooledStringIOǁrollover__mutmut_4, 
        'xǁSpooledStringIOǁrollover__mutmut_5': xǁSpooledStringIOǁrollover__mutmut_5, 
        'xǁSpooledStringIOǁrollover__mutmut_6': xǁSpooledStringIOǁrollover__mutmut_6, 
        'xǁSpooledStringIOǁrollover__mutmut_7': xǁSpooledStringIOǁrollover__mutmut_7, 
        'xǁSpooledStringIOǁrollover__mutmut_8': xǁSpooledStringIOǁrollover__mutmut_8, 
        'xǁSpooledStringIOǁrollover__mutmut_9': xǁSpooledStringIOǁrollover__mutmut_9, 
        'xǁSpooledStringIOǁrollover__mutmut_10': xǁSpooledStringIOǁrollover__mutmut_10, 
        'xǁSpooledStringIOǁrollover__mutmut_11': xǁSpooledStringIOǁrollover__mutmut_11, 
        'xǁSpooledStringIOǁrollover__mutmut_12': xǁSpooledStringIOǁrollover__mutmut_12, 
        'xǁSpooledStringIOǁrollover__mutmut_13': xǁSpooledStringIOǁrollover__mutmut_13
    }
    
    def rollover(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSpooledStringIOǁrollover__mutmut_orig"), object.__getattribute__(self, "xǁSpooledStringIOǁrollover__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rollover.__signature__ = _mutmut_signature(xǁSpooledStringIOǁrollover__mutmut_orig)
    xǁSpooledStringIOǁrollover__mutmut_orig.__name__ = 'xǁSpooledStringIOǁrollover'

    def tell(self):
        """Return the codepoint position"""
        self._checkClosed()
        return self._tell

    @property
    def len(self):
        """Determine the number of codepoints in the file"""
        pos = self.buffer.tell()
        self.buffer.seek(0)
        total = 0
        while True:
            ret = self.read(READ_CHUNK_SIZE)
            if not ret:
                break
            total += len(ret)
        self.buffer.seek(pos)
        return total


def x_is_text_fileobj__mutmut_orig(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_1(fileobj):
    if getattr(None, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_2(fileobj):
    if getattr(fileobj, None, False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_3(fileobj):
    if getattr(fileobj, 'encoding', None):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_4(fileobj):
    if getattr('encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_5(fileobj):
    if getattr(fileobj, False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_6(fileobj):
    if getattr(fileobj, 'encoding', ):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_7(fileobj):
    if getattr(fileobj, 'XXencodingXX', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_8(fileobj):
    if getattr(fileobj, 'ENCODING', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_9(fileobj):
    if getattr(fileobj, 'encoding', True):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_10(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return False
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_11(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(None, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_12(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, None, False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_13(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', None):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_14(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr('getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_15(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_16(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', ):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_17(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'XXgetvalueXX', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_18(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'GETVALUE', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_19(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', True):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_20(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return False
        except Exception:
            pass
    return False


def x_is_text_fileobj__mutmut_21(fileobj):
    if getattr(fileobj, 'encoding', False):
        # codecs.open and io.TextIOBase
        return True
    if getattr(fileobj, 'getvalue', False):
        # StringIO.StringIO / io.StringIO
        try:
            if isinstance(fileobj.getvalue(), str):
                return True
        except Exception:
            pass
    return True

x_is_text_fileobj__mutmut_mutants : ClassVar[MutantDict] = {
'x_is_text_fileobj__mutmut_1': x_is_text_fileobj__mutmut_1, 
    'x_is_text_fileobj__mutmut_2': x_is_text_fileobj__mutmut_2, 
    'x_is_text_fileobj__mutmut_3': x_is_text_fileobj__mutmut_3, 
    'x_is_text_fileobj__mutmut_4': x_is_text_fileobj__mutmut_4, 
    'x_is_text_fileobj__mutmut_5': x_is_text_fileobj__mutmut_5, 
    'x_is_text_fileobj__mutmut_6': x_is_text_fileobj__mutmut_6, 
    'x_is_text_fileobj__mutmut_7': x_is_text_fileobj__mutmut_7, 
    'x_is_text_fileobj__mutmut_8': x_is_text_fileobj__mutmut_8, 
    'x_is_text_fileobj__mutmut_9': x_is_text_fileobj__mutmut_9, 
    'x_is_text_fileobj__mutmut_10': x_is_text_fileobj__mutmut_10, 
    'x_is_text_fileobj__mutmut_11': x_is_text_fileobj__mutmut_11, 
    'x_is_text_fileobj__mutmut_12': x_is_text_fileobj__mutmut_12, 
    'x_is_text_fileobj__mutmut_13': x_is_text_fileobj__mutmut_13, 
    'x_is_text_fileobj__mutmut_14': x_is_text_fileobj__mutmut_14, 
    'x_is_text_fileobj__mutmut_15': x_is_text_fileobj__mutmut_15, 
    'x_is_text_fileobj__mutmut_16': x_is_text_fileobj__mutmut_16, 
    'x_is_text_fileobj__mutmut_17': x_is_text_fileobj__mutmut_17, 
    'x_is_text_fileobj__mutmut_18': x_is_text_fileobj__mutmut_18, 
    'x_is_text_fileobj__mutmut_19': x_is_text_fileobj__mutmut_19, 
    'x_is_text_fileobj__mutmut_20': x_is_text_fileobj__mutmut_20, 
    'x_is_text_fileobj__mutmut_21': x_is_text_fileobj__mutmut_21
}

def is_text_fileobj(*args, **kwargs):
    result = _mutmut_trampoline(x_is_text_fileobj__mutmut_orig, x_is_text_fileobj__mutmut_mutants, args, kwargs)
    return result 

is_text_fileobj.__signature__ = _mutmut_signature(x_is_text_fileobj__mutmut_orig)
x_is_text_fileobj__mutmut_orig.__name__ = 'x_is_text_fileobj'


class MultiFileReader:
    """Takes a list of open files or file-like objects and provides an
    interface to read from them all contiguously. Like
    :func:`itertools.chain()`, but for reading files.

       >>> mfr = MultiFileReader(BytesIO(b'ab'), BytesIO(b'cd'), BytesIO(b'e'))
       >>> mfr.read(3).decode('ascii')
       u'abc'
       >>> mfr.read(3).decode('ascii')
       u'de'

    The constructor takes as many fileobjs as you hand it, and will
    raise a TypeError on non-file-like objects. A ValueError is raised
    when file-like objects are a mix of bytes- and text-handling
    objects (for instance, BytesIO and StringIO).
    """

    def xǁMultiFileReaderǁ__init____mutmut_orig(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_1(self, *fileobjs):
        if all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_2(self, *fileobjs):
        if not all(None):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_3(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) or callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_4(self, *fileobjs):
        if not all([callable(None) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_5(self, *fileobjs):
        if not all([callable(getattr(None, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_6(self, *fileobjs):
        if not all([callable(getattr(f, None, None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_7(self, *fileobjs):
        if not all([callable(getattr('read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_8(self, *fileobjs):
        if not all([callable(getattr(f, None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_9(self, *fileobjs):
        if not all([callable(getattr(f, 'read', )) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_10(self, *fileobjs):
        if not all([callable(getattr(f, 'XXreadXX', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_11(self, *fileobjs):
        if not all([callable(getattr(f, 'READ', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_12(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(None) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_13(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(None, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_14(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, None, None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_15(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr('seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_16(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_17(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', )) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_18(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'XXseekXX', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_19(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'SEEK', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_20(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError(None)
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_21(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('XXMultiFileReader expected file-like objectsXX'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_22(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('multifilereader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_23(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MULTIFILEREADER EXPECTED FILE-LIKE OBJECTS'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_24(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            'XX with .read() and .seek()XX')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_25(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' WITH .READ() AND .SEEK()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_26(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all(None):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_27(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(None) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_28(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = None
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_29(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = 'XXXX'
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_30(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any(None):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_31(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(None) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_32(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError(None)
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_33(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('XXAll arguments to MultiFileReader must handleXX'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_34(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('all arguments to multifilereader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_35(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('ALL ARGUMENTS TO MULTIFILEREADER MUST HANDLE'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_36(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             'XX bytes OR text, not a mixXX')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_37(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes or text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_38(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' BYTES OR TEXT, NOT A MIX')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_39(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = None
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_40(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b'XXXX'
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_41(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_42(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_43(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = None
        self._index = 0

    def xǁMultiFileReaderǁ__init____mutmut_44(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = None

    def xǁMultiFileReaderǁ__init____mutmut_45(self, *fileobjs):
        if not all([callable(getattr(f, 'read', None)) and
                    callable(getattr(f, 'seek', None)) for f in fileobjs]):
            raise TypeError('MultiFileReader expected file-like objects'
                            ' with .read() and .seek()')
        if all([is_text_fileobj(f) for f in fileobjs]):
            # codecs.open and io.TextIOBase
            self._joiner = ''
        elif any([is_text_fileobj(f) for f in fileobjs]):
            raise ValueError('All arguments to MultiFileReader must handle'
                             ' bytes OR text, not a mix')
        else:
            # open/file and io.BytesIO
            self._joiner = b''
        self._fileobjs = fileobjs
        self._index = 1
    
    xǁMultiFileReaderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiFileReaderǁ__init____mutmut_1': xǁMultiFileReaderǁ__init____mutmut_1, 
        'xǁMultiFileReaderǁ__init____mutmut_2': xǁMultiFileReaderǁ__init____mutmut_2, 
        'xǁMultiFileReaderǁ__init____mutmut_3': xǁMultiFileReaderǁ__init____mutmut_3, 
        'xǁMultiFileReaderǁ__init____mutmut_4': xǁMultiFileReaderǁ__init____mutmut_4, 
        'xǁMultiFileReaderǁ__init____mutmut_5': xǁMultiFileReaderǁ__init____mutmut_5, 
        'xǁMultiFileReaderǁ__init____mutmut_6': xǁMultiFileReaderǁ__init____mutmut_6, 
        'xǁMultiFileReaderǁ__init____mutmut_7': xǁMultiFileReaderǁ__init____mutmut_7, 
        'xǁMultiFileReaderǁ__init____mutmut_8': xǁMultiFileReaderǁ__init____mutmut_8, 
        'xǁMultiFileReaderǁ__init____mutmut_9': xǁMultiFileReaderǁ__init____mutmut_9, 
        'xǁMultiFileReaderǁ__init____mutmut_10': xǁMultiFileReaderǁ__init____mutmut_10, 
        'xǁMultiFileReaderǁ__init____mutmut_11': xǁMultiFileReaderǁ__init____mutmut_11, 
        'xǁMultiFileReaderǁ__init____mutmut_12': xǁMultiFileReaderǁ__init____mutmut_12, 
        'xǁMultiFileReaderǁ__init____mutmut_13': xǁMultiFileReaderǁ__init____mutmut_13, 
        'xǁMultiFileReaderǁ__init____mutmut_14': xǁMultiFileReaderǁ__init____mutmut_14, 
        'xǁMultiFileReaderǁ__init____mutmut_15': xǁMultiFileReaderǁ__init____mutmut_15, 
        'xǁMultiFileReaderǁ__init____mutmut_16': xǁMultiFileReaderǁ__init____mutmut_16, 
        'xǁMultiFileReaderǁ__init____mutmut_17': xǁMultiFileReaderǁ__init____mutmut_17, 
        'xǁMultiFileReaderǁ__init____mutmut_18': xǁMultiFileReaderǁ__init____mutmut_18, 
        'xǁMultiFileReaderǁ__init____mutmut_19': xǁMultiFileReaderǁ__init____mutmut_19, 
        'xǁMultiFileReaderǁ__init____mutmut_20': xǁMultiFileReaderǁ__init____mutmut_20, 
        'xǁMultiFileReaderǁ__init____mutmut_21': xǁMultiFileReaderǁ__init____mutmut_21, 
        'xǁMultiFileReaderǁ__init____mutmut_22': xǁMultiFileReaderǁ__init____mutmut_22, 
        'xǁMultiFileReaderǁ__init____mutmut_23': xǁMultiFileReaderǁ__init____mutmut_23, 
        'xǁMultiFileReaderǁ__init____mutmut_24': xǁMultiFileReaderǁ__init____mutmut_24, 
        'xǁMultiFileReaderǁ__init____mutmut_25': xǁMultiFileReaderǁ__init____mutmut_25, 
        'xǁMultiFileReaderǁ__init____mutmut_26': xǁMultiFileReaderǁ__init____mutmut_26, 
        'xǁMultiFileReaderǁ__init____mutmut_27': xǁMultiFileReaderǁ__init____mutmut_27, 
        'xǁMultiFileReaderǁ__init____mutmut_28': xǁMultiFileReaderǁ__init____mutmut_28, 
        'xǁMultiFileReaderǁ__init____mutmut_29': xǁMultiFileReaderǁ__init____mutmut_29, 
        'xǁMultiFileReaderǁ__init____mutmut_30': xǁMultiFileReaderǁ__init____mutmut_30, 
        'xǁMultiFileReaderǁ__init____mutmut_31': xǁMultiFileReaderǁ__init____mutmut_31, 
        'xǁMultiFileReaderǁ__init____mutmut_32': xǁMultiFileReaderǁ__init____mutmut_32, 
        'xǁMultiFileReaderǁ__init____mutmut_33': xǁMultiFileReaderǁ__init____mutmut_33, 
        'xǁMultiFileReaderǁ__init____mutmut_34': xǁMultiFileReaderǁ__init____mutmut_34, 
        'xǁMultiFileReaderǁ__init____mutmut_35': xǁMultiFileReaderǁ__init____mutmut_35, 
        'xǁMultiFileReaderǁ__init____mutmut_36': xǁMultiFileReaderǁ__init____mutmut_36, 
        'xǁMultiFileReaderǁ__init____mutmut_37': xǁMultiFileReaderǁ__init____mutmut_37, 
        'xǁMultiFileReaderǁ__init____mutmut_38': xǁMultiFileReaderǁ__init____mutmut_38, 
        'xǁMultiFileReaderǁ__init____mutmut_39': xǁMultiFileReaderǁ__init____mutmut_39, 
        'xǁMultiFileReaderǁ__init____mutmut_40': xǁMultiFileReaderǁ__init____mutmut_40, 
        'xǁMultiFileReaderǁ__init____mutmut_41': xǁMultiFileReaderǁ__init____mutmut_41, 
        'xǁMultiFileReaderǁ__init____mutmut_42': xǁMultiFileReaderǁ__init____mutmut_42, 
        'xǁMultiFileReaderǁ__init____mutmut_43': xǁMultiFileReaderǁ__init____mutmut_43, 
        'xǁMultiFileReaderǁ__init____mutmut_44': xǁMultiFileReaderǁ__init____mutmut_44, 
        'xǁMultiFileReaderǁ__init____mutmut_45': xǁMultiFileReaderǁ__init____mutmut_45
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiFileReaderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMultiFileReaderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMultiFileReaderǁ__init____mutmut_orig)
    xǁMultiFileReaderǁ__init____mutmut_orig.__name__ = 'xǁMultiFileReaderǁ__init__'

    def xǁMultiFileReaderǁread__mutmut_orig(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_1(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_2(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(None)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_3(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = None
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_4(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 or self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_5(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt >= 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_6(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 1 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_7(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index <= len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_8(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(None)
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_9(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(None))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_10(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = None
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_11(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got <= amt:
                self._index += 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_12(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index = 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_13(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index -= 1
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_14(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 2
            amt -= got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_15(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt = got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_16(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt += got
        return self._joiner.join(parts)

    def xǁMultiFileReaderǁread__mutmut_17(self, amt=None):
        """Read up to the specified *amt*, seamlessly bridging across
        files. Returns the appropriate type of string (bytes or text)
        for the input, and returns an empty string when the files are
        exhausted.
        """
        if not amt:
            return self._joiner.join(f.read() for f in self._fileobjs)
        parts = []
        while amt > 0 and self._index < len(self._fileobjs):
            parts.append(self._fileobjs[self._index].read(amt))
            got = len(parts[-1])
            if got < amt:
                self._index += 1
            amt -= got
        return self._joiner.join(None)
    
    xǁMultiFileReaderǁread__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiFileReaderǁread__mutmut_1': xǁMultiFileReaderǁread__mutmut_1, 
        'xǁMultiFileReaderǁread__mutmut_2': xǁMultiFileReaderǁread__mutmut_2, 
        'xǁMultiFileReaderǁread__mutmut_3': xǁMultiFileReaderǁread__mutmut_3, 
        'xǁMultiFileReaderǁread__mutmut_4': xǁMultiFileReaderǁread__mutmut_4, 
        'xǁMultiFileReaderǁread__mutmut_5': xǁMultiFileReaderǁread__mutmut_5, 
        'xǁMultiFileReaderǁread__mutmut_6': xǁMultiFileReaderǁread__mutmut_6, 
        'xǁMultiFileReaderǁread__mutmut_7': xǁMultiFileReaderǁread__mutmut_7, 
        'xǁMultiFileReaderǁread__mutmut_8': xǁMultiFileReaderǁread__mutmut_8, 
        'xǁMultiFileReaderǁread__mutmut_9': xǁMultiFileReaderǁread__mutmut_9, 
        'xǁMultiFileReaderǁread__mutmut_10': xǁMultiFileReaderǁread__mutmut_10, 
        'xǁMultiFileReaderǁread__mutmut_11': xǁMultiFileReaderǁread__mutmut_11, 
        'xǁMultiFileReaderǁread__mutmut_12': xǁMultiFileReaderǁread__mutmut_12, 
        'xǁMultiFileReaderǁread__mutmut_13': xǁMultiFileReaderǁread__mutmut_13, 
        'xǁMultiFileReaderǁread__mutmut_14': xǁMultiFileReaderǁread__mutmut_14, 
        'xǁMultiFileReaderǁread__mutmut_15': xǁMultiFileReaderǁread__mutmut_15, 
        'xǁMultiFileReaderǁread__mutmut_16': xǁMultiFileReaderǁread__mutmut_16, 
        'xǁMultiFileReaderǁread__mutmut_17': xǁMultiFileReaderǁread__mutmut_17
    }
    
    def read(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiFileReaderǁread__mutmut_orig"), object.__getattribute__(self, "xǁMultiFileReaderǁread__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read.__signature__ = _mutmut_signature(xǁMultiFileReaderǁread__mutmut_orig)
    xǁMultiFileReaderǁread__mutmut_orig.__name__ = 'xǁMultiFileReaderǁread'

    def xǁMultiFileReaderǁseek__mutmut_orig(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_1(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence == os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_2(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                None)
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_3(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'XXMultiFileReader.seek() only supports os.SEEK_SETXX')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_4(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'multifilereader.seek() only supports os.seek_set')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_5(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MULTIFILEREADER.SEEK() ONLY SUPPORTS OS.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_6(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset == 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_7(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 1:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_8(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                None)
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_9(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'XXMultiFileReader only supports seeking to start at this timeXX')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_10(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'multifilereader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_11(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MULTIFILEREADER ONLY SUPPORTS SEEKING TO START AT THIS TIME')
        for f in self._fileobjs:
            f.seek(0)

    def xǁMultiFileReaderǁseek__mutmut_12(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(None)

    def xǁMultiFileReaderǁseek__mutmut_13(self, offset, whence=os.SEEK_SET):
        """Enables setting position of the file cursor to a given
        *offset*. Currently only supports ``offset=0``.
        """
        if whence != os.SEEK_SET:
            raise NotImplementedError(
                'MultiFileReader.seek() only supports os.SEEK_SET')
        if offset != 0:
            raise NotImplementedError(
                'MultiFileReader only supports seeking to start at this time')
        for f in self._fileobjs:
            f.seek(1)
    
    xǁMultiFileReaderǁseek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiFileReaderǁseek__mutmut_1': xǁMultiFileReaderǁseek__mutmut_1, 
        'xǁMultiFileReaderǁseek__mutmut_2': xǁMultiFileReaderǁseek__mutmut_2, 
        'xǁMultiFileReaderǁseek__mutmut_3': xǁMultiFileReaderǁseek__mutmut_3, 
        'xǁMultiFileReaderǁseek__mutmut_4': xǁMultiFileReaderǁseek__mutmut_4, 
        'xǁMultiFileReaderǁseek__mutmut_5': xǁMultiFileReaderǁseek__mutmut_5, 
        'xǁMultiFileReaderǁseek__mutmut_6': xǁMultiFileReaderǁseek__mutmut_6, 
        'xǁMultiFileReaderǁseek__mutmut_7': xǁMultiFileReaderǁseek__mutmut_7, 
        'xǁMultiFileReaderǁseek__mutmut_8': xǁMultiFileReaderǁseek__mutmut_8, 
        'xǁMultiFileReaderǁseek__mutmut_9': xǁMultiFileReaderǁseek__mutmut_9, 
        'xǁMultiFileReaderǁseek__mutmut_10': xǁMultiFileReaderǁseek__mutmut_10, 
        'xǁMultiFileReaderǁseek__mutmut_11': xǁMultiFileReaderǁseek__mutmut_11, 
        'xǁMultiFileReaderǁseek__mutmut_12': xǁMultiFileReaderǁseek__mutmut_12, 
        'xǁMultiFileReaderǁseek__mutmut_13': xǁMultiFileReaderǁseek__mutmut_13
    }
    
    def seek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiFileReaderǁseek__mutmut_orig"), object.__getattribute__(self, "xǁMultiFileReaderǁseek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    seek.__signature__ = _mutmut_signature(xǁMultiFileReaderǁseek__mutmut_orig)
    xǁMultiFileReaderǁseek__mutmut_orig.__name__ = 'xǁMultiFileReaderǁseek'
