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

"""Virtually every Python programmer has used Python for wrangling
disk contents, and ``fileutils`` collects solutions to some of the
most commonly-found gaps in the standard library.
"""


import os
import re
import sys
import stat
import errno
import fnmatch
from shutil import copy2, copystat, Error


__all__ = ['mkdir_p', 'atomic_save', 'AtomicSaver', 'FilePerms',
           'iter_find_files', 'copytree']


FULL_PERMS = 0o777
RW_PERMS = 438
_SINGLE_FULL_PERM = 7
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


def x_mkdir_p__mutmut_orig(path):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
    return


def x_mkdir_p__mutmut_1(path):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    try:
        os.makedirs(None)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
    return


def x_mkdir_p__mutmut_2(path):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST or os.path.isdir(path):
            return
        raise
    return


def x_mkdir_p__mutmut_3(path):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST and os.path.isdir(path):
            return
        raise
    return


def x_mkdir_p__mutmut_4(path):
    """Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of the ``mkdir -p``
    command available in Linux/BSD environments, but also works on
    Windows.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(None):
            return
        raise
    return

x_mkdir_p__mutmut_mutants : ClassVar[MutantDict] = {
'x_mkdir_p__mutmut_1': x_mkdir_p__mutmut_1, 
    'x_mkdir_p__mutmut_2': x_mkdir_p__mutmut_2, 
    'x_mkdir_p__mutmut_3': x_mkdir_p__mutmut_3, 
    'x_mkdir_p__mutmut_4': x_mkdir_p__mutmut_4
}

def mkdir_p(*args, **kwargs):
    result = _mutmut_trampoline(x_mkdir_p__mutmut_orig, x_mkdir_p__mutmut_mutants, args, kwargs)
    return result 

mkdir_p.__signature__ = _mutmut_signature(x_mkdir_p__mutmut_orig)
x_mkdir_p__mutmut_orig.__name__ = 'x_mkdir_p'


class FilePerms:
    """The :class:`FilePerms` type is used to represent standard POSIX
    filesystem permissions:

      * Read
      * Write
      * Execute

    Across three classes of user:

      * Owning (u)ser
      * Owner's (g)roup
      * Any (o)ther user

    This class assists with computing new permissions, as well as
    working with numeric octal ``777``-style and ``rwx``-style
    permissions. Currently it only considers the bottom 9 permission
    bits; it does not support sticky bits or more advanced permission
    systems.

    Args:
        user (str): A string in the 'rwx' format, omitting characters
            for which owning user's permissions are not provided.
        group (str): A string in the 'rwx' format, omitting characters
            for which owning group permissions are not provided.
        other (str): A string in the 'rwx' format, omitting characters
            for which owning other/world permissions are not provided.

    There are many ways to use :class:`FilePerms`:

    >>> FilePerms(user='rwx', group='xrw', other='wxr')  # note character order
    FilePerms(user='rwx', group='rwx', other='rwx')
    >>> int(FilePerms('r', 'r', ''))
    288
    >>> oct(288)[-3:]  # XXX Py3k
    '440'

    See also the :meth:`FilePerms.from_int` and
    :meth:`FilePerms.from_path` classmethods for useful alternative
    ways to construct :class:`FilePerms` objects.
    """
    # TODO: consider more than the lower 9 bits
    class _FilePermProperty:
        _perm_chars = 'rwx'
        _perm_set = frozenset('rwx')
        _perm_val = {'r': 4, 'w': 2, 'x': 1}  # for sorting

        def __init__(self, attribute, offset):
            self.attribute = attribute
            self.offset = offset

        def __get__(self, fp_obj, type_=None):
            if fp_obj is None:
                return self
            return getattr(fp_obj, self.attribute)

        def __set__(self, fp_obj, value):
            cur = getattr(fp_obj, self.attribute)
            if cur == value:
                return
            try:
                invalid_chars = set(str(value)) - self._perm_set
            except TypeError:
                raise TypeError('expected string, not %r' % value)
            if invalid_chars:
                raise ValueError('got invalid chars %r in permission'
                                 ' specification %r, expected empty string'
                                 ' or one or more of %r'
                                 % (invalid_chars, value, self._perm_chars))

            def sort_key(c): return self._perm_val[c]
            new_value = ''.join(sorted(set(value),
                                       key=sort_key, reverse=True))
            setattr(fp_obj, self.attribute, new_value)
            self._update_integer(fp_obj, new_value)

        def _update_integer(self, fp_obj, value):
            mode = 0
            key = 'xwr'
            for symbol in value:
                bit = 2 ** key.index(symbol)
                mode |= (bit << (self.offset * 3))
            fp_obj._integer |= mode

    def xǁFilePermsǁ__init____mutmut_orig(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_1(self, user='XXXX', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_2(self, user='', group='XXXX', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_3(self, user='', group='', other='XXXX'):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_4(self, user='', group='', other=''):
        self._user, self._group, self._other = None
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_5(self, user='', group='', other=''):
        self._user, self._group, self._other = 'XXXX', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_6(self, user='', group='', other=''):
        self._user, self._group, self._other = '', 'XXXX', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_7(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', 'XXXX'
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_8(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = None
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_9(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 1
        self.user = user
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_10(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = None
        self.group = group
        self.other = other

    def xǁFilePermsǁ__init____mutmut_11(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = None
        self.other = other

    def xǁFilePermsǁ__init____mutmut_12(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = None
    
    xǁFilePermsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFilePermsǁ__init____mutmut_1': xǁFilePermsǁ__init____mutmut_1, 
        'xǁFilePermsǁ__init____mutmut_2': xǁFilePermsǁ__init____mutmut_2, 
        'xǁFilePermsǁ__init____mutmut_3': xǁFilePermsǁ__init____mutmut_3, 
        'xǁFilePermsǁ__init____mutmut_4': xǁFilePermsǁ__init____mutmut_4, 
        'xǁFilePermsǁ__init____mutmut_5': xǁFilePermsǁ__init____mutmut_5, 
        'xǁFilePermsǁ__init____mutmut_6': xǁFilePermsǁ__init____mutmut_6, 
        'xǁFilePermsǁ__init____mutmut_7': xǁFilePermsǁ__init____mutmut_7, 
        'xǁFilePermsǁ__init____mutmut_8': xǁFilePermsǁ__init____mutmut_8, 
        'xǁFilePermsǁ__init____mutmut_9': xǁFilePermsǁ__init____mutmut_9, 
        'xǁFilePermsǁ__init____mutmut_10': xǁFilePermsǁ__init____mutmut_10, 
        'xǁFilePermsǁ__init____mutmut_11': xǁFilePermsǁ__init____mutmut_11, 
        'xǁFilePermsǁ__init____mutmut_12': xǁFilePermsǁ__init____mutmut_12
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFilePermsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁFilePermsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁFilePermsǁ__init____mutmut_orig)
    xǁFilePermsǁ__init____mutmut_orig.__name__ = 'xǁFilePermsǁ__init__'

    @classmethod
    def from_int(cls, i):
        """Create a :class:`FilePerms` object from an integer.

        >>> FilePerms.from_int(0o644)  # note the leading zero-oh for octal
        FilePerms(user='rw', group='r', other='r')
        """
        i &= FULL_PERMS
        key = ('', 'x', 'w', 'xw', 'r', 'rx', 'rw', 'rwx')
        parts = []
        while i:
            parts.append(key[i & _SINGLE_FULL_PERM])
            i >>= 3
        parts.reverse()
        return cls(*parts)

    @classmethod
    def from_path(cls, path):
        """Make a new :class:`FilePerms` object based on the permissions
        assigned to the file or directory at *path*.

        Args:
            path (str): Filesystem path of the target file.

        Here's an example that holds true on most systems:

        >>> import tempfile
        >>> 'r' in FilePerms.from_path(tempfile.gettempdir()).user
        True
        """
        stat_res = os.stat(path)
        return cls.from_int(stat.S_IMODE(stat_res.st_mode))

    def __int__(self):
        return self._integer

    # Sphinx tip: attribute docstrings come after the attribute
    user = _FilePermProperty('_user', 2)
    "Stores the ``rwx``-formatted *user* permission."
    group = _FilePermProperty('_group', 1)
    "Stores the ``rwx``-formatted *group* permission."
    other = _FilePermProperty('_other', 0)
    "Stores the ``rwx``-formatted *other* permission."

    def xǁFilePermsǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return ('%s(user=%r, group=%r, other=%r)'
                % (cn, self.user, self.group, self.other))

    def xǁFilePermsǁ__repr____mutmut_1(self):
        cn = None
        return ('%s(user=%r, group=%r, other=%r)'
                % (cn, self.user, self.group, self.other))

    def xǁFilePermsǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        return ('%s(user=%r, group=%r, other=%r)' / (cn, self.user, self.group, self.other))

    def xǁFilePermsǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        return ('XX%s(user=%r, group=%r, other=%r)XX'
                % (cn, self.user, self.group, self.other))

    def xǁFilePermsǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        return ('%S(USER=%R, GROUP=%R, OTHER=%R)'
                % (cn, self.user, self.group, self.other))
    
    xǁFilePermsǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFilePermsǁ__repr____mutmut_1': xǁFilePermsǁ__repr____mutmut_1, 
        'xǁFilePermsǁ__repr____mutmut_2': xǁFilePermsǁ__repr____mutmut_2, 
        'xǁFilePermsǁ__repr____mutmut_3': xǁFilePermsǁ__repr____mutmut_3, 
        'xǁFilePermsǁ__repr____mutmut_4': xǁFilePermsǁ__repr____mutmut_4
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFilePermsǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁFilePermsǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁFilePermsǁ__repr____mutmut_orig)
    xǁFilePermsǁ__repr____mutmut_orig.__name__ = 'xǁFilePermsǁ__repr__'

####


_TEXT_OPENFLAGS = os.O_RDWR | os.O_CREAT | os.O_EXCL
if hasattr(os, 'O_NOINHERIT'):
    _TEXT_OPENFLAGS |= os.O_NOINHERIT
if hasattr(os, 'O_NOFOLLOW'):
    _TEXT_OPENFLAGS |= os.O_NOFOLLOW
_BIN_OPENFLAGS = _TEXT_OPENFLAGS
if hasattr(os, 'O_BINARY'):
    _BIN_OPENFLAGS |= os.O_BINARY


try:
    import fcntl as fcntl
except ImportError:
    def set_cloexec(fd):
        "Dummy set_cloexec for platforms without fcntl support"
        pass
else:
    def set_cloexec(fd):
        """Does a best-effort :func:`fcntl.fcntl` call to set a fd to be
        automatically closed by any future child processes.

        Implementation from the :mod:`tempfile` module.
        """
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFD, 0)
        except OSError:
            pass
        else:
            # flags read successfully, modify
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(fd, fcntl.F_SETFD, flags)
        return


def x_atomic_save__mutmut_orig(dest_path, **kwargs):
    """A convenient interface to the :class:`AtomicSaver` type. Example:

    >>> try:
    ...     with atomic_save("file.txt", text_mode=True) as fo:
    ...         _ = fo.write('bye')
    ...         1/0  # will error
    ...         fo.write('bye')
    ... except ZeroDivisionError:
    ...     pass  # at least our file.txt didn't get overwritten

    See the :class:`AtomicSaver` documentation for details.
    """
    return AtomicSaver(dest_path, **kwargs)


def x_atomic_save__mutmut_1(dest_path, **kwargs):
    """A convenient interface to the :class:`AtomicSaver` type. Example:

    >>> try:
    ...     with atomic_save("file.txt", text_mode=True) as fo:
    ...         _ = fo.write('bye')
    ...         1/0  # will error
    ...         fo.write('bye')
    ... except ZeroDivisionError:
    ...     pass  # at least our file.txt didn't get overwritten

    See the :class:`AtomicSaver` documentation for details.
    """
    return AtomicSaver(None, **kwargs)


def x_atomic_save__mutmut_2(dest_path, **kwargs):
    """A convenient interface to the :class:`AtomicSaver` type. Example:

    >>> try:
    ...     with atomic_save("file.txt", text_mode=True) as fo:
    ...         _ = fo.write('bye')
    ...         1/0  # will error
    ...         fo.write('bye')
    ... except ZeroDivisionError:
    ...     pass  # at least our file.txt didn't get overwritten

    See the :class:`AtomicSaver` documentation for details.
    """
    return AtomicSaver(**kwargs)


def x_atomic_save__mutmut_3(dest_path, **kwargs):
    """A convenient interface to the :class:`AtomicSaver` type. Example:

    >>> try:
    ...     with atomic_save("file.txt", text_mode=True) as fo:
    ...         _ = fo.write('bye')
    ...         1/0  # will error
    ...         fo.write('bye')
    ... except ZeroDivisionError:
    ...     pass  # at least our file.txt didn't get overwritten

    See the :class:`AtomicSaver` documentation for details.
    """
    return AtomicSaver(dest_path, )

x_atomic_save__mutmut_mutants : ClassVar[MutantDict] = {
'x_atomic_save__mutmut_1': x_atomic_save__mutmut_1, 
    'x_atomic_save__mutmut_2': x_atomic_save__mutmut_2, 
    'x_atomic_save__mutmut_3': x_atomic_save__mutmut_3
}

def atomic_save(*args, **kwargs):
    result = _mutmut_trampoline(x_atomic_save__mutmut_orig, x_atomic_save__mutmut_mutants, args, kwargs)
    return result 

atomic_save.__signature__ = _mutmut_signature(x_atomic_save__mutmut_orig)
x_atomic_save__mutmut_orig.__name__ = 'x_atomic_save'


def x_path_to_unicode__mutmut_orig(path):
    if isinstance(path, str):
        return path
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    return path.decode(encoding)


def x_path_to_unicode__mutmut_1(path):
    if isinstance(path, str):
        return path
    encoding = None
    return path.decode(encoding)


def x_path_to_unicode__mutmut_2(path):
    if isinstance(path, str):
        return path
    encoding = sys.getfilesystemencoding() and sys.getdefaultencoding()
    return path.decode(encoding)


def x_path_to_unicode__mutmut_3(path):
    if isinstance(path, str):
        return path
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    return path.decode(None)

x_path_to_unicode__mutmut_mutants : ClassVar[MutantDict] = {
'x_path_to_unicode__mutmut_1': x_path_to_unicode__mutmut_1, 
    'x_path_to_unicode__mutmut_2': x_path_to_unicode__mutmut_2, 
    'x_path_to_unicode__mutmut_3': x_path_to_unicode__mutmut_3
}

def path_to_unicode(*args, **kwargs):
    result = _mutmut_trampoline(x_path_to_unicode__mutmut_orig, x_path_to_unicode__mutmut_mutants, args, kwargs)
    return result 

path_to_unicode.__signature__ = _mutmut_signature(x_path_to_unicode__mutmut_orig)
x_path_to_unicode__mutmut_orig.__name__ = 'x_path_to_unicode'


if os.name == 'nt':
    import ctypes
    from ctypes import c_wchar_p
    from ctypes.wintypes import DWORD, LPVOID

    _ReplaceFile = ctypes.windll.kernel32.ReplaceFile
    _ReplaceFile.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p,
                             DWORD, LPVOID, LPVOID]

    def replace(src, dst):
        # argument names match stdlib docs, docstring below
        try:
            # ReplaceFile fails if the dest file does not exist, so
            # first try to rename it into position
            os.rename(src, dst)
            return
        except OSError as we:
            if we.errno == errno.EEXIST:
                pass  # continue with the ReplaceFile logic below
            else:
                raise

        src = path_to_unicode(src)
        dst = path_to_unicode(dst)
        res = _ReplaceFile(c_wchar_p(dst), c_wchar_p(src),
                           None, 0, None, None)
        if not res:
            raise OSError(f'failed to replace {dst!r} with {src!r}')
        return

    def atomic_rename(src, dst, overwrite=False):
        "Rename *src* to *dst*, replacing *dst* if *overwrite is True"
        if overwrite:
            replace(src, dst)
        else:
            os.rename(src, dst)
        return
else:
    # wrapper func for cross compat + docs
    def replace(src, dst):
        # os.replace does the same thing on unix
        return os.rename(src, dst)

    def atomic_rename(src, dst, overwrite=False):
        "Rename *src* to *dst*, replacing *dst* if *overwrite is True"
        if overwrite:
            os.rename(src, dst)
        else:
            os.link(src, dst)
            os.unlink(src)
        return


_atomic_rename = atomic_rename  # backwards compat

replace.__doc__ = """Similar to :func:`os.replace` in Python 3.3+,
this function will atomically create or replace the file at path
*dst* with the file at path *src*.

On Windows, this function uses the ReplaceFile API for maximum
possible atomicity on a range of filesystems.
"""


class AtomicSaver:
    """``AtomicSaver`` is a configurable `context manager`_ that provides
    a writable :class:`file` which will be moved into place as long as
    no exceptions are raised within the context manager's block. These
    "part files" are created in the same directory as the destination
    path to ensure atomic move operations (i.e., no cross-filesystem
    moves occur).

    Args:
        dest_path (str): The path where the completed file will be
            written.
        overwrite (bool): Whether to overwrite the destination file if
            it exists at completion time. Defaults to ``True``.
        file_perms (int): Integer representation of file permissions
            for the newly-created file. Defaults are, when the
            destination path already exists, to copy the permissions
            from the previous file, or if the file did not exist, to
            respect the user's configured `umask`_, usually resulting
            in octal 0644 or 0664.
        text_mode (bool): Whether to open the destination file in text
            mode (i.e., ``'w'`` not ``'wb'``). Defaults to ``False`` (``wb``).
        part_file (str): Name of the temporary *part_file*. Defaults
            to *dest_path* + ``.part``. Note that this argument is
            just the filename, and not the full path of the part
            file. To guarantee atomic saves, part files are always
            created in the same directory as the destination path.
        overwrite_part (bool): Whether to overwrite the *part_file*,
            should it exist at setup time. Defaults to ``False``,
            which results in an :exc:`OSError` being raised on
            pre-existing part files. Be careful of setting this to
            ``True`` in situations when multiple threads or processes
            could be writing to the same part file.
        rm_part_on_exc (bool): Remove *part_file* on exception cases.
            Defaults to ``True``, but ``False`` can be useful for
            recovery in some cases. Note that resumption is not
            automatic and by default an :exc:`OSError` is raised if
            the *part_file* exists.

    Practically, the AtomicSaver serves a few purposes:

      * Avoiding overwriting an existing, valid file with a partially
        written one.
      * Providing a reasonable guarantee that a part file only has one
        writer at a time.
      * Optional recovery of partial data in failure cases.

    .. _context manager: https://docs.python.org/2/reference/compound_stmts.html#with
    .. _umask: https://en.wikipedia.org/wiki/Umask

    """
    _default_file_perms = RW_PERMS

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_orig(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_1(self, dest_path, **kwargs):
        self.dest_path = None
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_2(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = None
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_3(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop(None, True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_4(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', None)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_5(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop(True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_6(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', )
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_7(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('XXoverwriteXX', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_8(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('OVERWRITE', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_9(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', False)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_10(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = None
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_11(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop(None, None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_12(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop(None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_13(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', )
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_14(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('XXfile_permsXX', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_15(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('FILE_PERMS', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_16(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = None
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_17(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop(None, False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_18(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', None)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_19(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop(False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_20(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', )
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_21(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('XXoverwrite_partXX', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_22(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('OVERWRITE_PART', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_23(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', True)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_24(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = None
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_25(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop(None, None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_26(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop(None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_27(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', )
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_28(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('XXpart_fileXX', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_29(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('PART_FILE', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_30(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = None
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_31(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop(None, True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_32(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', None)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_33(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop(True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_34(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', )
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_35(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('XXrm_part_on_excXX', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_36(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('RM_PART_ON_EXC', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_37(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', False)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_38(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = None
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_39(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop(None, False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_40(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', None)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_41(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop(False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_42(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', )
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_43(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('XXtext_modeXX', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_44(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('TEXT_MODE', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_45(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', True)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_46(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = None
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_47(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop(None, -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_48(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', None)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_49(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop(-1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_50(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', )
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_51(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('XXbufferingXX', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_52(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('BUFFERING', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_53(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', +1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_54(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -2)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_55(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(None)

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_56(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = None
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_57(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(None)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_58(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = None
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_59(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(None)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_60(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_61(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = None
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_62(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path - '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_63(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + 'XX.partXX'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_64(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.PART'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_65(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = None
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_66(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(None, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_67(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, None)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_68(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_69(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, )
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_70(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = None
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_71(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'XXw+XX' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_72(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'W+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_73(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'XXw+bXX'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_74(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'W+B'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_75(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = None

        self.part_file = None

    # TODO: option to abort if target file modify date has changed since start?
    def xǁAtomicSaverǁ__init____mutmut_76(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.file_perms = kwargs.pop('file_perms', None)
        self.overwrite_part = kwargs.pop('overwrite_part', False)
        self.part_filename = kwargs.pop('part_file', None)
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self.text_mode = kwargs.pop('text_mode', False)
        self.buffering = kwargs.pop('buffering', -1)
        if kwargs:
            raise TypeError(f'unexpected kwargs: {kwargs.keys()!r}')

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_filename)
        self.mode = 'w+' if self.text_mode else 'w+b'
        self.open_flags = _TEXT_OPENFLAGS if self.text_mode else _BIN_OPENFLAGS

        self.part_file = ""
    
    xǁAtomicSaverǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAtomicSaverǁ__init____mutmut_1': xǁAtomicSaverǁ__init____mutmut_1, 
        'xǁAtomicSaverǁ__init____mutmut_2': xǁAtomicSaverǁ__init____mutmut_2, 
        'xǁAtomicSaverǁ__init____mutmut_3': xǁAtomicSaverǁ__init____mutmut_3, 
        'xǁAtomicSaverǁ__init____mutmut_4': xǁAtomicSaverǁ__init____mutmut_4, 
        'xǁAtomicSaverǁ__init____mutmut_5': xǁAtomicSaverǁ__init____mutmut_5, 
        'xǁAtomicSaverǁ__init____mutmut_6': xǁAtomicSaverǁ__init____mutmut_6, 
        'xǁAtomicSaverǁ__init____mutmut_7': xǁAtomicSaverǁ__init____mutmut_7, 
        'xǁAtomicSaverǁ__init____mutmut_8': xǁAtomicSaverǁ__init____mutmut_8, 
        'xǁAtomicSaverǁ__init____mutmut_9': xǁAtomicSaverǁ__init____mutmut_9, 
        'xǁAtomicSaverǁ__init____mutmut_10': xǁAtomicSaverǁ__init____mutmut_10, 
        'xǁAtomicSaverǁ__init____mutmut_11': xǁAtomicSaverǁ__init____mutmut_11, 
        'xǁAtomicSaverǁ__init____mutmut_12': xǁAtomicSaverǁ__init____mutmut_12, 
        'xǁAtomicSaverǁ__init____mutmut_13': xǁAtomicSaverǁ__init____mutmut_13, 
        'xǁAtomicSaverǁ__init____mutmut_14': xǁAtomicSaverǁ__init____mutmut_14, 
        'xǁAtomicSaverǁ__init____mutmut_15': xǁAtomicSaverǁ__init____mutmut_15, 
        'xǁAtomicSaverǁ__init____mutmut_16': xǁAtomicSaverǁ__init____mutmut_16, 
        'xǁAtomicSaverǁ__init____mutmut_17': xǁAtomicSaverǁ__init____mutmut_17, 
        'xǁAtomicSaverǁ__init____mutmut_18': xǁAtomicSaverǁ__init____mutmut_18, 
        'xǁAtomicSaverǁ__init____mutmut_19': xǁAtomicSaverǁ__init____mutmut_19, 
        'xǁAtomicSaverǁ__init____mutmut_20': xǁAtomicSaverǁ__init____mutmut_20, 
        'xǁAtomicSaverǁ__init____mutmut_21': xǁAtomicSaverǁ__init____mutmut_21, 
        'xǁAtomicSaverǁ__init____mutmut_22': xǁAtomicSaverǁ__init____mutmut_22, 
        'xǁAtomicSaverǁ__init____mutmut_23': xǁAtomicSaverǁ__init____mutmut_23, 
        'xǁAtomicSaverǁ__init____mutmut_24': xǁAtomicSaverǁ__init____mutmut_24, 
        'xǁAtomicSaverǁ__init____mutmut_25': xǁAtomicSaverǁ__init____mutmut_25, 
        'xǁAtomicSaverǁ__init____mutmut_26': xǁAtomicSaverǁ__init____mutmut_26, 
        'xǁAtomicSaverǁ__init____mutmut_27': xǁAtomicSaverǁ__init____mutmut_27, 
        'xǁAtomicSaverǁ__init____mutmut_28': xǁAtomicSaverǁ__init____mutmut_28, 
        'xǁAtomicSaverǁ__init____mutmut_29': xǁAtomicSaverǁ__init____mutmut_29, 
        'xǁAtomicSaverǁ__init____mutmut_30': xǁAtomicSaverǁ__init____mutmut_30, 
        'xǁAtomicSaverǁ__init____mutmut_31': xǁAtomicSaverǁ__init____mutmut_31, 
        'xǁAtomicSaverǁ__init____mutmut_32': xǁAtomicSaverǁ__init____mutmut_32, 
        'xǁAtomicSaverǁ__init____mutmut_33': xǁAtomicSaverǁ__init____mutmut_33, 
        'xǁAtomicSaverǁ__init____mutmut_34': xǁAtomicSaverǁ__init____mutmut_34, 
        'xǁAtomicSaverǁ__init____mutmut_35': xǁAtomicSaverǁ__init____mutmut_35, 
        'xǁAtomicSaverǁ__init____mutmut_36': xǁAtomicSaverǁ__init____mutmut_36, 
        'xǁAtomicSaverǁ__init____mutmut_37': xǁAtomicSaverǁ__init____mutmut_37, 
        'xǁAtomicSaverǁ__init____mutmut_38': xǁAtomicSaverǁ__init____mutmut_38, 
        'xǁAtomicSaverǁ__init____mutmut_39': xǁAtomicSaverǁ__init____mutmut_39, 
        'xǁAtomicSaverǁ__init____mutmut_40': xǁAtomicSaverǁ__init____mutmut_40, 
        'xǁAtomicSaverǁ__init____mutmut_41': xǁAtomicSaverǁ__init____mutmut_41, 
        'xǁAtomicSaverǁ__init____mutmut_42': xǁAtomicSaverǁ__init____mutmut_42, 
        'xǁAtomicSaverǁ__init____mutmut_43': xǁAtomicSaverǁ__init____mutmut_43, 
        'xǁAtomicSaverǁ__init____mutmut_44': xǁAtomicSaverǁ__init____mutmut_44, 
        'xǁAtomicSaverǁ__init____mutmut_45': xǁAtomicSaverǁ__init____mutmut_45, 
        'xǁAtomicSaverǁ__init____mutmut_46': xǁAtomicSaverǁ__init____mutmut_46, 
        'xǁAtomicSaverǁ__init____mutmut_47': xǁAtomicSaverǁ__init____mutmut_47, 
        'xǁAtomicSaverǁ__init____mutmut_48': xǁAtomicSaverǁ__init____mutmut_48, 
        'xǁAtomicSaverǁ__init____mutmut_49': xǁAtomicSaverǁ__init____mutmut_49, 
        'xǁAtomicSaverǁ__init____mutmut_50': xǁAtomicSaverǁ__init____mutmut_50, 
        'xǁAtomicSaverǁ__init____mutmut_51': xǁAtomicSaverǁ__init____mutmut_51, 
        'xǁAtomicSaverǁ__init____mutmut_52': xǁAtomicSaverǁ__init____mutmut_52, 
        'xǁAtomicSaverǁ__init____mutmut_53': xǁAtomicSaverǁ__init____mutmut_53, 
        'xǁAtomicSaverǁ__init____mutmut_54': xǁAtomicSaverǁ__init____mutmut_54, 
        'xǁAtomicSaverǁ__init____mutmut_55': xǁAtomicSaverǁ__init____mutmut_55, 
        'xǁAtomicSaverǁ__init____mutmut_56': xǁAtomicSaverǁ__init____mutmut_56, 
        'xǁAtomicSaverǁ__init____mutmut_57': xǁAtomicSaverǁ__init____mutmut_57, 
        'xǁAtomicSaverǁ__init____mutmut_58': xǁAtomicSaverǁ__init____mutmut_58, 
        'xǁAtomicSaverǁ__init____mutmut_59': xǁAtomicSaverǁ__init____mutmut_59, 
        'xǁAtomicSaverǁ__init____mutmut_60': xǁAtomicSaverǁ__init____mutmut_60, 
        'xǁAtomicSaverǁ__init____mutmut_61': xǁAtomicSaverǁ__init____mutmut_61, 
        'xǁAtomicSaverǁ__init____mutmut_62': xǁAtomicSaverǁ__init____mutmut_62, 
        'xǁAtomicSaverǁ__init____mutmut_63': xǁAtomicSaverǁ__init____mutmut_63, 
        'xǁAtomicSaverǁ__init____mutmut_64': xǁAtomicSaverǁ__init____mutmut_64, 
        'xǁAtomicSaverǁ__init____mutmut_65': xǁAtomicSaverǁ__init____mutmut_65, 
        'xǁAtomicSaverǁ__init____mutmut_66': xǁAtomicSaverǁ__init____mutmut_66, 
        'xǁAtomicSaverǁ__init____mutmut_67': xǁAtomicSaverǁ__init____mutmut_67, 
        'xǁAtomicSaverǁ__init____mutmut_68': xǁAtomicSaverǁ__init____mutmut_68, 
        'xǁAtomicSaverǁ__init____mutmut_69': xǁAtomicSaverǁ__init____mutmut_69, 
        'xǁAtomicSaverǁ__init____mutmut_70': xǁAtomicSaverǁ__init____mutmut_70, 
        'xǁAtomicSaverǁ__init____mutmut_71': xǁAtomicSaverǁ__init____mutmut_71, 
        'xǁAtomicSaverǁ__init____mutmut_72': xǁAtomicSaverǁ__init____mutmut_72, 
        'xǁAtomicSaverǁ__init____mutmut_73': xǁAtomicSaverǁ__init____mutmut_73, 
        'xǁAtomicSaverǁ__init____mutmut_74': xǁAtomicSaverǁ__init____mutmut_74, 
        'xǁAtomicSaverǁ__init____mutmut_75': xǁAtomicSaverǁ__init____mutmut_75, 
        'xǁAtomicSaverǁ__init____mutmut_76': xǁAtomicSaverǁ__init____mutmut_76
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAtomicSaverǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAtomicSaverǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAtomicSaverǁ__init____mutmut_orig)
    xǁAtomicSaverǁ__init____mutmut_orig.__name__ = 'xǁAtomicSaverǁ__init__'

    def xǁAtomicSaverǁ_open_part_file__mutmut_orig(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_1(self):
        do_chmod = None
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_2(self):
        do_chmod = False
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_3(self):
        do_chmod = True
        file_perms = None
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_4(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is not None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_5(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = None
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_6(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(None)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_7(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = None
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_8(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(None)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_9(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = None
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_10(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = None  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_11(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = True  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_12(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = None
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_13(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(None, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_14(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, None, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_15(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, None)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_16(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_17(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_18(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, )
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_19(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(None)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_20(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = None

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_21(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(None, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_22(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, None, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_23(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, None)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_24(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_25(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_26(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, )

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_27(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(None, file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_28(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, None)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_29(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(file_perms)
            except OSError:
                self.part_file.close()
                raise
        return

    def xǁAtomicSaverǁ_open_part_file__mutmut_30(self):
        do_chmod = True
        file_perms = self.file_perms
        if file_perms is None:
            try:
                # try to copy from file being replaced
                stat_res = os.stat(self.dest_path)
                file_perms = stat.S_IMODE(stat_res.st_mode)
            except OSError:
                # default if no destination file exists
                file_perms = self._default_file_perms
                do_chmod = False  # respect the umask

        fd = os.open(self.part_path, self.open_flags, file_perms)
        set_cloexec(fd)
        self.part_file = os.fdopen(fd, self.mode, self.buffering)

        # if default perms are overridden by the user or previous dest_path
        # chmod away the effects of the umask
        if do_chmod:
            try:
                os.chmod(self.part_path, )
            except OSError:
                self.part_file.close()
                raise
        return
    
    xǁAtomicSaverǁ_open_part_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAtomicSaverǁ_open_part_file__mutmut_1': xǁAtomicSaverǁ_open_part_file__mutmut_1, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_2': xǁAtomicSaverǁ_open_part_file__mutmut_2, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_3': xǁAtomicSaverǁ_open_part_file__mutmut_3, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_4': xǁAtomicSaverǁ_open_part_file__mutmut_4, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_5': xǁAtomicSaverǁ_open_part_file__mutmut_5, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_6': xǁAtomicSaverǁ_open_part_file__mutmut_6, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_7': xǁAtomicSaverǁ_open_part_file__mutmut_7, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_8': xǁAtomicSaverǁ_open_part_file__mutmut_8, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_9': xǁAtomicSaverǁ_open_part_file__mutmut_9, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_10': xǁAtomicSaverǁ_open_part_file__mutmut_10, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_11': xǁAtomicSaverǁ_open_part_file__mutmut_11, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_12': xǁAtomicSaverǁ_open_part_file__mutmut_12, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_13': xǁAtomicSaverǁ_open_part_file__mutmut_13, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_14': xǁAtomicSaverǁ_open_part_file__mutmut_14, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_15': xǁAtomicSaverǁ_open_part_file__mutmut_15, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_16': xǁAtomicSaverǁ_open_part_file__mutmut_16, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_17': xǁAtomicSaverǁ_open_part_file__mutmut_17, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_18': xǁAtomicSaverǁ_open_part_file__mutmut_18, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_19': xǁAtomicSaverǁ_open_part_file__mutmut_19, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_20': xǁAtomicSaverǁ_open_part_file__mutmut_20, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_21': xǁAtomicSaverǁ_open_part_file__mutmut_21, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_22': xǁAtomicSaverǁ_open_part_file__mutmut_22, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_23': xǁAtomicSaverǁ_open_part_file__mutmut_23, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_24': xǁAtomicSaverǁ_open_part_file__mutmut_24, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_25': xǁAtomicSaverǁ_open_part_file__mutmut_25, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_26': xǁAtomicSaverǁ_open_part_file__mutmut_26, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_27': xǁAtomicSaverǁ_open_part_file__mutmut_27, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_28': xǁAtomicSaverǁ_open_part_file__mutmut_28, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_29': xǁAtomicSaverǁ_open_part_file__mutmut_29, 
        'xǁAtomicSaverǁ_open_part_file__mutmut_30': xǁAtomicSaverǁ_open_part_file__mutmut_30
    }
    
    def _open_part_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAtomicSaverǁ_open_part_file__mutmut_orig"), object.__getattribute__(self, "xǁAtomicSaverǁ_open_part_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _open_part_file.__signature__ = _mutmut_signature(xǁAtomicSaverǁ_open_part_file__mutmut_orig)
    xǁAtomicSaverǁ_open_part_file__mutmut_orig.__name__ = 'xǁAtomicSaverǁ_open_part_file'

    def xǁAtomicSaverǁsetup__mutmut_orig(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_1(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(None):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_2(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_3(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(None,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_4(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              None,
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_5(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              None)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_6(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError('Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_7(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_8(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              )
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_9(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'XXOverwrite disabled and file already existsXX',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_10(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_11(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'OVERWRITE DISABLED AND FILE ALREADY EXISTS',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_12(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part or os.path.lexists(self.part_path):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_13(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(None):
            os.unlink(self.part_path)
        self._open_part_file()
        return

    def xǁAtomicSaverǁsetup__mutmut_14(self):
        """Called on context manager entry (the :keyword:`with` statement),
        the ``setup()`` method creates the temporary file in the same
        directory as the destination file.

        ``setup()`` tests for a writable directory with rename permissions
        early, as the part file may not be written to immediately (not
        using :func:`os.access` because of the potential issues of
        effective vs. real privileges).

        If the caller is not using the :class:`AtomicSaver` as a
        context manager, this method should be called explicitly
        before writing.
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        if self.overwrite_part and os.path.lexists(self.part_path):
            os.unlink(None)
        self._open_part_file()
        return
    
    xǁAtomicSaverǁsetup__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAtomicSaverǁsetup__mutmut_1': xǁAtomicSaverǁsetup__mutmut_1, 
        'xǁAtomicSaverǁsetup__mutmut_2': xǁAtomicSaverǁsetup__mutmut_2, 
        'xǁAtomicSaverǁsetup__mutmut_3': xǁAtomicSaverǁsetup__mutmut_3, 
        'xǁAtomicSaverǁsetup__mutmut_4': xǁAtomicSaverǁsetup__mutmut_4, 
        'xǁAtomicSaverǁsetup__mutmut_5': xǁAtomicSaverǁsetup__mutmut_5, 
        'xǁAtomicSaverǁsetup__mutmut_6': xǁAtomicSaverǁsetup__mutmut_6, 
        'xǁAtomicSaverǁsetup__mutmut_7': xǁAtomicSaverǁsetup__mutmut_7, 
        'xǁAtomicSaverǁsetup__mutmut_8': xǁAtomicSaverǁsetup__mutmut_8, 
        'xǁAtomicSaverǁsetup__mutmut_9': xǁAtomicSaverǁsetup__mutmut_9, 
        'xǁAtomicSaverǁsetup__mutmut_10': xǁAtomicSaverǁsetup__mutmut_10, 
        'xǁAtomicSaverǁsetup__mutmut_11': xǁAtomicSaverǁsetup__mutmut_11, 
        'xǁAtomicSaverǁsetup__mutmut_12': xǁAtomicSaverǁsetup__mutmut_12, 
        'xǁAtomicSaverǁsetup__mutmut_13': xǁAtomicSaverǁsetup__mutmut_13, 
        'xǁAtomicSaverǁsetup__mutmut_14': xǁAtomicSaverǁsetup__mutmut_14
    }
    
    def setup(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAtomicSaverǁsetup__mutmut_orig"), object.__getattribute__(self, "xǁAtomicSaverǁsetup__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setup.__signature__ = _mutmut_signature(xǁAtomicSaverǁsetup__mutmut_orig)
    xǁAtomicSaverǁsetup__mutmut_orig.__name__ = 'xǁAtomicSaverǁsetup'

    def __enter__(self):
        self.setup()
        return self.part_file

    def xǁAtomicSaverǁ__exit____mutmut_orig(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_1(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(None)
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_2(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(None)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_3(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(None, self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_4(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, None,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_5(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          overwrite=None)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_6(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_7(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_8(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          )
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return

    def xǁAtomicSaverǁ__exit____mutmut_9(self, exc_type, exc_val, exc_tb):
        if self.part_file:
            # Ensure data is flushed and synced to disk before closing
            self.part_file.flush()
            os.fsync(self.part_file.fileno())
            self.part_file.close()
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except Exception:
                    pass  # avoid masking original error
            return
        try:
            atomic_rename(self.part_path, self.dest_path,
                          overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                try:
                    os.unlink(None)
                except Exception:
                    pass  # avoid masking original error
            raise  # could not save destination file
        return
    
    xǁAtomicSaverǁ__exit____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAtomicSaverǁ__exit____mutmut_1': xǁAtomicSaverǁ__exit____mutmut_1, 
        'xǁAtomicSaverǁ__exit____mutmut_2': xǁAtomicSaverǁ__exit____mutmut_2, 
        'xǁAtomicSaverǁ__exit____mutmut_3': xǁAtomicSaverǁ__exit____mutmut_3, 
        'xǁAtomicSaverǁ__exit____mutmut_4': xǁAtomicSaverǁ__exit____mutmut_4, 
        'xǁAtomicSaverǁ__exit____mutmut_5': xǁAtomicSaverǁ__exit____mutmut_5, 
        'xǁAtomicSaverǁ__exit____mutmut_6': xǁAtomicSaverǁ__exit____mutmut_6, 
        'xǁAtomicSaverǁ__exit____mutmut_7': xǁAtomicSaverǁ__exit____mutmut_7, 
        'xǁAtomicSaverǁ__exit____mutmut_8': xǁAtomicSaverǁ__exit____mutmut_8, 
        'xǁAtomicSaverǁ__exit____mutmut_9': xǁAtomicSaverǁ__exit____mutmut_9
    }
    
    def __exit__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAtomicSaverǁ__exit____mutmut_orig"), object.__getattribute__(self, "xǁAtomicSaverǁ__exit____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __exit__.__signature__ = _mutmut_signature(xǁAtomicSaverǁ__exit____mutmut_orig)
    xǁAtomicSaverǁ__exit____mutmut_orig.__name__ = 'xǁAtomicSaverǁ__exit__'


def x_iter_find_files__mutmut_orig(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_1(directory, patterns, ignored=None, include_dirs=True, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_2(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = None
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_3(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = None

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_4(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile(None)

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_5(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join(None))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_6(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('XX|XX'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_7(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(None) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_8(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_9(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = None
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_10(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = None
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_11(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = None
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_12(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile(None)
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_13(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join(None))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_14(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('XX|XX'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_15(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(None) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_16(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = None
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_17(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(None):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_18(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None or (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_19(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_20(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) + start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_21(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) >= max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_22(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            break
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_23(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(None):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_24(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored or ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_25(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(None):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_26(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        break
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_27(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = None
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_28(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(None, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_29(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, None)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_30(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_31(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, )
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_32(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(None):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_33(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored or ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_34(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(None):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_35(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    break
                filename = os.path.join(root, basename)
                yield filename
    return


def x_iter_find_files__mutmut_36(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = None
                yield filename
    return


def x_iter_find_files__mutmut_37(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(None, basename)
                yield filename
    return


def x_iter_find_files__mutmut_38(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, None)
                yield filename
    return


def x_iter_find_files__mutmut_39(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(basename)
                yield filename
    return


def x_iter_find_files__mutmut_40(directory, patterns, ignored=None, include_dirs=False, max_depth=None):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.
        include_dirs (bool): Whether to include directories that match
           patterns, as well. Defaults to ``False``.
        max_depth (int): traverse up to this level of subdirectory.
           I.e., 0 for the specified *directory* only, 1 for *directory* 
           and one level of subdirectory.

    For example, finding Python files in the current directory:

    >>> _CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, str):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    start_depth = len(directory.split(os.path.sep))
    for root, dirs, files in os.walk(directory):
        if max_depth is not None and (len(root.split(os.path.sep)) - start_depth) > max_depth:
            continue
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, )
                yield filename
    return

x_iter_find_files__mutmut_mutants : ClassVar[MutantDict] = {
'x_iter_find_files__mutmut_1': x_iter_find_files__mutmut_1, 
    'x_iter_find_files__mutmut_2': x_iter_find_files__mutmut_2, 
    'x_iter_find_files__mutmut_3': x_iter_find_files__mutmut_3, 
    'x_iter_find_files__mutmut_4': x_iter_find_files__mutmut_4, 
    'x_iter_find_files__mutmut_5': x_iter_find_files__mutmut_5, 
    'x_iter_find_files__mutmut_6': x_iter_find_files__mutmut_6, 
    'x_iter_find_files__mutmut_7': x_iter_find_files__mutmut_7, 
    'x_iter_find_files__mutmut_8': x_iter_find_files__mutmut_8, 
    'x_iter_find_files__mutmut_9': x_iter_find_files__mutmut_9, 
    'x_iter_find_files__mutmut_10': x_iter_find_files__mutmut_10, 
    'x_iter_find_files__mutmut_11': x_iter_find_files__mutmut_11, 
    'x_iter_find_files__mutmut_12': x_iter_find_files__mutmut_12, 
    'x_iter_find_files__mutmut_13': x_iter_find_files__mutmut_13, 
    'x_iter_find_files__mutmut_14': x_iter_find_files__mutmut_14, 
    'x_iter_find_files__mutmut_15': x_iter_find_files__mutmut_15, 
    'x_iter_find_files__mutmut_16': x_iter_find_files__mutmut_16, 
    'x_iter_find_files__mutmut_17': x_iter_find_files__mutmut_17, 
    'x_iter_find_files__mutmut_18': x_iter_find_files__mutmut_18, 
    'x_iter_find_files__mutmut_19': x_iter_find_files__mutmut_19, 
    'x_iter_find_files__mutmut_20': x_iter_find_files__mutmut_20, 
    'x_iter_find_files__mutmut_21': x_iter_find_files__mutmut_21, 
    'x_iter_find_files__mutmut_22': x_iter_find_files__mutmut_22, 
    'x_iter_find_files__mutmut_23': x_iter_find_files__mutmut_23, 
    'x_iter_find_files__mutmut_24': x_iter_find_files__mutmut_24, 
    'x_iter_find_files__mutmut_25': x_iter_find_files__mutmut_25, 
    'x_iter_find_files__mutmut_26': x_iter_find_files__mutmut_26, 
    'x_iter_find_files__mutmut_27': x_iter_find_files__mutmut_27, 
    'x_iter_find_files__mutmut_28': x_iter_find_files__mutmut_28, 
    'x_iter_find_files__mutmut_29': x_iter_find_files__mutmut_29, 
    'x_iter_find_files__mutmut_30': x_iter_find_files__mutmut_30, 
    'x_iter_find_files__mutmut_31': x_iter_find_files__mutmut_31, 
    'x_iter_find_files__mutmut_32': x_iter_find_files__mutmut_32, 
    'x_iter_find_files__mutmut_33': x_iter_find_files__mutmut_33, 
    'x_iter_find_files__mutmut_34': x_iter_find_files__mutmut_34, 
    'x_iter_find_files__mutmut_35': x_iter_find_files__mutmut_35, 
    'x_iter_find_files__mutmut_36': x_iter_find_files__mutmut_36, 
    'x_iter_find_files__mutmut_37': x_iter_find_files__mutmut_37, 
    'x_iter_find_files__mutmut_38': x_iter_find_files__mutmut_38, 
    'x_iter_find_files__mutmut_39': x_iter_find_files__mutmut_39, 
    'x_iter_find_files__mutmut_40': x_iter_find_files__mutmut_40
}

def iter_find_files(*args, **kwargs):
    result = _mutmut_trampoline(x_iter_find_files__mutmut_orig, x_iter_find_files__mutmut_mutants, args, kwargs)
    return result 

iter_find_files.__signature__ = _mutmut_signature(x_iter_find_files__mutmut_orig)
x_iter_find_files__mutmut_orig.__name__ = 'x_iter_find_files'


def x_copy_tree__mutmut_orig(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_1(src, dst, symlinks=True, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_2(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = None
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_3(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(None)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_4(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_5(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = None
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_6(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(None, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_7(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, None)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_8(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_9(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, )
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_10(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = None

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_11(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(None)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_12(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = None
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_13(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name not in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_14(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            break
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_15(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = None
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_16(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(None, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_17(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, None)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_18(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_19(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, )
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_20(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = None
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_21(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(None, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_22(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, None)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_23(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_24(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, )
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_25(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks or os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_26(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(None):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_27(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = None
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_28(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(None)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_29(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(None, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_30(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, None)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_31(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_32(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, )
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_33(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(None):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_34(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(None, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_35(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, None, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_36(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, None, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_37(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, None)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_38(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_39(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_40(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_41(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, )
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_42(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(None, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_43(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, None)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_44(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_45(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, )
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_46(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(None)
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_47(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[1])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_48(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append(None)
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_49(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(None)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_50(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(None, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_51(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, None)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_52(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_53(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, )
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_54(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append(None)
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_55(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(None)))
    if errors:
        raise Error(errors)


def x_copy_tree__mutmut_56(src, dst, symlinks=False, ignore=None):
    """The ``copy_tree`` function is an exact copy of the built-in
    :func:`shutil.copytree`, with one key difference: it will not
    raise an exception if part of the tree already exists. It achieves
    this by using :func:`mkdir_p`.

    As of Python 3.8, you may pass :func:`shutil.copytree` the
    `dirs_exist_ok=True` flag to achieve the same effect.

    Args:
        src (str): Path of the source directory to copy.
        dst (str): Destination path. Existing directories accepted.
        symlinks (bool): If ``True``, copy symlinks rather than their
            contents.
        ignore (callable): A callable that takes a path and directory
            listing, returning the files within the listing to be ignored.

    For more details, check out :func:`shutil.copytree` and
    :func:`shutil.copy2`.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.append((src, dst, str(why)))
    if errors:
        raise Error(None)

x_copy_tree__mutmut_mutants : ClassVar[MutantDict] = {
'x_copy_tree__mutmut_1': x_copy_tree__mutmut_1, 
    'x_copy_tree__mutmut_2': x_copy_tree__mutmut_2, 
    'x_copy_tree__mutmut_3': x_copy_tree__mutmut_3, 
    'x_copy_tree__mutmut_4': x_copy_tree__mutmut_4, 
    'x_copy_tree__mutmut_5': x_copy_tree__mutmut_5, 
    'x_copy_tree__mutmut_6': x_copy_tree__mutmut_6, 
    'x_copy_tree__mutmut_7': x_copy_tree__mutmut_7, 
    'x_copy_tree__mutmut_8': x_copy_tree__mutmut_8, 
    'x_copy_tree__mutmut_9': x_copy_tree__mutmut_9, 
    'x_copy_tree__mutmut_10': x_copy_tree__mutmut_10, 
    'x_copy_tree__mutmut_11': x_copy_tree__mutmut_11, 
    'x_copy_tree__mutmut_12': x_copy_tree__mutmut_12, 
    'x_copy_tree__mutmut_13': x_copy_tree__mutmut_13, 
    'x_copy_tree__mutmut_14': x_copy_tree__mutmut_14, 
    'x_copy_tree__mutmut_15': x_copy_tree__mutmut_15, 
    'x_copy_tree__mutmut_16': x_copy_tree__mutmut_16, 
    'x_copy_tree__mutmut_17': x_copy_tree__mutmut_17, 
    'x_copy_tree__mutmut_18': x_copy_tree__mutmut_18, 
    'x_copy_tree__mutmut_19': x_copy_tree__mutmut_19, 
    'x_copy_tree__mutmut_20': x_copy_tree__mutmut_20, 
    'x_copy_tree__mutmut_21': x_copy_tree__mutmut_21, 
    'x_copy_tree__mutmut_22': x_copy_tree__mutmut_22, 
    'x_copy_tree__mutmut_23': x_copy_tree__mutmut_23, 
    'x_copy_tree__mutmut_24': x_copy_tree__mutmut_24, 
    'x_copy_tree__mutmut_25': x_copy_tree__mutmut_25, 
    'x_copy_tree__mutmut_26': x_copy_tree__mutmut_26, 
    'x_copy_tree__mutmut_27': x_copy_tree__mutmut_27, 
    'x_copy_tree__mutmut_28': x_copy_tree__mutmut_28, 
    'x_copy_tree__mutmut_29': x_copy_tree__mutmut_29, 
    'x_copy_tree__mutmut_30': x_copy_tree__mutmut_30, 
    'x_copy_tree__mutmut_31': x_copy_tree__mutmut_31, 
    'x_copy_tree__mutmut_32': x_copy_tree__mutmut_32, 
    'x_copy_tree__mutmut_33': x_copy_tree__mutmut_33, 
    'x_copy_tree__mutmut_34': x_copy_tree__mutmut_34, 
    'x_copy_tree__mutmut_35': x_copy_tree__mutmut_35, 
    'x_copy_tree__mutmut_36': x_copy_tree__mutmut_36, 
    'x_copy_tree__mutmut_37': x_copy_tree__mutmut_37, 
    'x_copy_tree__mutmut_38': x_copy_tree__mutmut_38, 
    'x_copy_tree__mutmut_39': x_copy_tree__mutmut_39, 
    'x_copy_tree__mutmut_40': x_copy_tree__mutmut_40, 
    'x_copy_tree__mutmut_41': x_copy_tree__mutmut_41, 
    'x_copy_tree__mutmut_42': x_copy_tree__mutmut_42, 
    'x_copy_tree__mutmut_43': x_copy_tree__mutmut_43, 
    'x_copy_tree__mutmut_44': x_copy_tree__mutmut_44, 
    'x_copy_tree__mutmut_45': x_copy_tree__mutmut_45, 
    'x_copy_tree__mutmut_46': x_copy_tree__mutmut_46, 
    'x_copy_tree__mutmut_47': x_copy_tree__mutmut_47, 
    'x_copy_tree__mutmut_48': x_copy_tree__mutmut_48, 
    'x_copy_tree__mutmut_49': x_copy_tree__mutmut_49, 
    'x_copy_tree__mutmut_50': x_copy_tree__mutmut_50, 
    'x_copy_tree__mutmut_51': x_copy_tree__mutmut_51, 
    'x_copy_tree__mutmut_52': x_copy_tree__mutmut_52, 
    'x_copy_tree__mutmut_53': x_copy_tree__mutmut_53, 
    'x_copy_tree__mutmut_54': x_copy_tree__mutmut_54, 
    'x_copy_tree__mutmut_55': x_copy_tree__mutmut_55, 
    'x_copy_tree__mutmut_56': x_copy_tree__mutmut_56
}

def copy_tree(*args, **kwargs):
    result = _mutmut_trampoline(x_copy_tree__mutmut_orig, x_copy_tree__mutmut_mutants, args, kwargs)
    return result 

copy_tree.__signature__ = _mutmut_signature(x_copy_tree__mutmut_orig)
x_copy_tree__mutmut_orig.__name__ = 'x_copy_tree'


copytree = copy_tree  # alias for drop-in replacement of shutil


# like open(os.devnull) but with even fewer side effects
class DummyFile:
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_orig(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_1(self, path, mode='XXrXX', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_2(self, path, mode='R', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_3(self, path, mode='r', buffering=None):
        self.name = None
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_4(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = None
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_5(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = None
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_6(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = True
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_7(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = ""
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_8(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = None
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_9(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = True
        self.encoding = None
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_10(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = ""
        self.newlines = None
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_11(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = ""
        self.softspace = 0
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_12(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = None
    # TODO: raise ValueErrors on closed for all methods?
    # TODO: enforce read/write
    def xǁDummyFileǁ__init____mutmut_13(self, path, mode='r', buffering=None):
        self.name = path
        self.mode = mode
        self.closed = False
        self.errors = None
        self.isatty = False
        self.encoding = None
        self.newlines = None
        self.softspace = 1
    
    xǁDummyFileǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁ__init____mutmut_1': xǁDummyFileǁ__init____mutmut_1, 
        'xǁDummyFileǁ__init____mutmut_2': xǁDummyFileǁ__init____mutmut_2, 
        'xǁDummyFileǁ__init____mutmut_3': xǁDummyFileǁ__init____mutmut_3, 
        'xǁDummyFileǁ__init____mutmut_4': xǁDummyFileǁ__init____mutmut_4, 
        'xǁDummyFileǁ__init____mutmut_5': xǁDummyFileǁ__init____mutmut_5, 
        'xǁDummyFileǁ__init____mutmut_6': xǁDummyFileǁ__init____mutmut_6, 
        'xǁDummyFileǁ__init____mutmut_7': xǁDummyFileǁ__init____mutmut_7, 
        'xǁDummyFileǁ__init____mutmut_8': xǁDummyFileǁ__init____mutmut_8, 
        'xǁDummyFileǁ__init____mutmut_9': xǁDummyFileǁ__init____mutmut_9, 
        'xǁDummyFileǁ__init____mutmut_10': xǁDummyFileǁ__init____mutmut_10, 
        'xǁDummyFileǁ__init____mutmut_11': xǁDummyFileǁ__init____mutmut_11, 
        'xǁDummyFileǁ__init____mutmut_12': xǁDummyFileǁ__init____mutmut_12, 
        'xǁDummyFileǁ__init____mutmut_13': xǁDummyFileǁ__init____mutmut_13
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDummyFileǁ__init____mutmut_orig)
    xǁDummyFileǁ__init____mutmut_orig.__name__ = 'xǁDummyFileǁ__init__'

    def xǁDummyFileǁclose__mutmut_orig(self):
        self.closed = True

    def xǁDummyFileǁclose__mutmut_1(self):
        self.closed = None

    def xǁDummyFileǁclose__mutmut_2(self):
        self.closed = False
    
    xǁDummyFileǁclose__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁclose__mutmut_1': xǁDummyFileǁclose__mutmut_1, 
        'xǁDummyFileǁclose__mutmut_2': xǁDummyFileǁclose__mutmut_2
    }
    
    def close(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁclose__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁclose__mutmut_mutants"), args, kwargs, self)
        return result 
    
    close.__signature__ = _mutmut_signature(xǁDummyFileǁclose__mutmut_orig)
    xǁDummyFileǁclose__mutmut_orig.__name__ = 'xǁDummyFileǁclose'

    def xǁDummyFileǁfileno__mutmut_orig(self):
        return -1

    def xǁDummyFileǁfileno__mutmut_1(self):
        return +1

    def xǁDummyFileǁfileno__mutmut_2(self):
        return -2
    
    xǁDummyFileǁfileno__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁfileno__mutmut_1': xǁDummyFileǁfileno__mutmut_1, 
        'xǁDummyFileǁfileno__mutmut_2': xǁDummyFileǁfileno__mutmut_2
    }
    
    def fileno(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁfileno__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁfileno__mutmut_mutants"), args, kwargs, self)
        return result 
    
    fileno.__signature__ = _mutmut_signature(xǁDummyFileǁfileno__mutmut_orig)
    xǁDummyFileǁfileno__mutmut_orig.__name__ = 'xǁDummyFileǁfileno'

    def xǁDummyFileǁflush__mutmut_orig(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁflush__mutmut_1(self):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁflush__mutmut_2(self):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁflush__mutmut_3(self):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁflush__mutmut_4(self):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁflush__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁflush__mutmut_1': xǁDummyFileǁflush__mutmut_1, 
        'xǁDummyFileǁflush__mutmut_2': xǁDummyFileǁflush__mutmut_2, 
        'xǁDummyFileǁflush__mutmut_3': xǁDummyFileǁflush__mutmut_3, 
        'xǁDummyFileǁflush__mutmut_4': xǁDummyFileǁflush__mutmut_4
    }
    
    def flush(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁflush__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁflush__mutmut_mutants"), args, kwargs, self)
        return result 
    
    flush.__signature__ = _mutmut_signature(xǁDummyFileǁflush__mutmut_orig)
    xǁDummyFileǁflush__mutmut_orig.__name__ = 'xǁDummyFileǁflush'

    def next(self):
        raise StopIteration()

    def xǁDummyFileǁread__mutmut_orig(self, size=0):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return ''

    def xǁDummyFileǁread__mutmut_1(self, size=1):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return ''

    def xǁDummyFileǁread__mutmut_2(self, size=0):
        if self.closed:
            raise ValueError(None)
        return ''

    def xǁDummyFileǁread__mutmut_3(self, size=0):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return ''

    def xǁDummyFileǁread__mutmut_4(self, size=0):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return ''

    def xǁDummyFileǁread__mutmut_5(self, size=0):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return ''

    def xǁDummyFileǁread__mutmut_6(self, size=0):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return 'XXXX'
    
    xǁDummyFileǁread__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁread__mutmut_1': xǁDummyFileǁread__mutmut_1, 
        'xǁDummyFileǁread__mutmut_2': xǁDummyFileǁread__mutmut_2, 
        'xǁDummyFileǁread__mutmut_3': xǁDummyFileǁread__mutmut_3, 
        'xǁDummyFileǁread__mutmut_4': xǁDummyFileǁread__mutmut_4, 
        'xǁDummyFileǁread__mutmut_5': xǁDummyFileǁread__mutmut_5, 
        'xǁDummyFileǁread__mutmut_6': xǁDummyFileǁread__mutmut_6
    }
    
    def read(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁread__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁread__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read.__signature__ = _mutmut_signature(xǁDummyFileǁread__mutmut_orig)
    xǁDummyFileǁread__mutmut_orig.__name__ = 'xǁDummyFileǁread'

    def xǁDummyFileǁreadline__mutmut_orig(self, size=0):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return ''

    def xǁDummyFileǁreadline__mutmut_1(self, size=1):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return ''

    def xǁDummyFileǁreadline__mutmut_2(self, size=0):
        if self.closed:
            raise ValueError(None)
        return ''

    def xǁDummyFileǁreadline__mutmut_3(self, size=0):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return ''

    def xǁDummyFileǁreadline__mutmut_4(self, size=0):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return ''

    def xǁDummyFileǁreadline__mutmut_5(self, size=0):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return ''

    def xǁDummyFileǁreadline__mutmut_6(self, size=0):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return 'XXXX'
    
    xǁDummyFileǁreadline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁreadline__mutmut_1': xǁDummyFileǁreadline__mutmut_1, 
        'xǁDummyFileǁreadline__mutmut_2': xǁDummyFileǁreadline__mutmut_2, 
        'xǁDummyFileǁreadline__mutmut_3': xǁDummyFileǁreadline__mutmut_3, 
        'xǁDummyFileǁreadline__mutmut_4': xǁDummyFileǁreadline__mutmut_4, 
        'xǁDummyFileǁreadline__mutmut_5': xǁDummyFileǁreadline__mutmut_5, 
        'xǁDummyFileǁreadline__mutmut_6': xǁDummyFileǁreadline__mutmut_6
    }
    
    def readline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁreadline__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁreadline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readline.__signature__ = _mutmut_signature(xǁDummyFileǁreadline__mutmut_orig)
    xǁDummyFileǁreadline__mutmut_orig.__name__ = 'xǁDummyFileǁreadline'

    def xǁDummyFileǁreadlines__mutmut_orig(self, size=0):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return []

    def xǁDummyFileǁreadlines__mutmut_1(self, size=1):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return []

    def xǁDummyFileǁreadlines__mutmut_2(self, size=0):
        if self.closed:
            raise ValueError(None)
        return []

    def xǁDummyFileǁreadlines__mutmut_3(self, size=0):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return []

    def xǁDummyFileǁreadlines__mutmut_4(self, size=0):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return []

    def xǁDummyFileǁreadlines__mutmut_5(self, size=0):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return []
    
    xǁDummyFileǁreadlines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁreadlines__mutmut_1': xǁDummyFileǁreadlines__mutmut_1, 
        'xǁDummyFileǁreadlines__mutmut_2': xǁDummyFileǁreadlines__mutmut_2, 
        'xǁDummyFileǁreadlines__mutmut_3': xǁDummyFileǁreadlines__mutmut_3, 
        'xǁDummyFileǁreadlines__mutmut_4': xǁDummyFileǁreadlines__mutmut_4, 
        'xǁDummyFileǁreadlines__mutmut_5': xǁDummyFileǁreadlines__mutmut_5
    }
    
    def readlines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁreadlines__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁreadlines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    readlines.__signature__ = _mutmut_signature(xǁDummyFileǁreadlines__mutmut_orig)
    xǁDummyFileǁreadlines__mutmut_orig.__name__ = 'xǁDummyFileǁreadlines'

    def xǁDummyFileǁseek__mutmut_orig(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁseek__mutmut_1(self):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁseek__mutmut_2(self):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁseek__mutmut_3(self):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁseek__mutmut_4(self):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁseek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁseek__mutmut_1': xǁDummyFileǁseek__mutmut_1, 
        'xǁDummyFileǁseek__mutmut_2': xǁDummyFileǁseek__mutmut_2, 
        'xǁDummyFileǁseek__mutmut_3': xǁDummyFileǁseek__mutmut_3, 
        'xǁDummyFileǁseek__mutmut_4': xǁDummyFileǁseek__mutmut_4
    }
    
    def seek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁseek__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁseek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    seek.__signature__ = _mutmut_signature(xǁDummyFileǁseek__mutmut_orig)
    xǁDummyFileǁseek__mutmut_orig.__name__ = 'xǁDummyFileǁseek'

    def xǁDummyFileǁtell__mutmut_orig(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return 0

    def xǁDummyFileǁtell__mutmut_1(self):
        if self.closed:
            raise ValueError(None)
        return 0

    def xǁDummyFileǁtell__mutmut_2(self):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return 0

    def xǁDummyFileǁtell__mutmut_3(self):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return 0

    def xǁDummyFileǁtell__mutmut_4(self):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return 0

    def xǁDummyFileǁtell__mutmut_5(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return 1
    
    xǁDummyFileǁtell__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁtell__mutmut_1': xǁDummyFileǁtell__mutmut_1, 
        'xǁDummyFileǁtell__mutmut_2': xǁDummyFileǁtell__mutmut_2, 
        'xǁDummyFileǁtell__mutmut_3': xǁDummyFileǁtell__mutmut_3, 
        'xǁDummyFileǁtell__mutmut_4': xǁDummyFileǁtell__mutmut_4, 
        'xǁDummyFileǁtell__mutmut_5': xǁDummyFileǁtell__mutmut_5
    }
    
    def tell(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁtell__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁtell__mutmut_mutants"), args, kwargs, self)
        return result 
    
    tell.__signature__ = _mutmut_signature(xǁDummyFileǁtell__mutmut_orig)
    xǁDummyFileǁtell__mutmut_orig.__name__ = 'xǁDummyFileǁtell'

    def xǁDummyFileǁtruncate__mutmut_orig(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁtruncate__mutmut_1(self):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁtruncate__mutmut_2(self):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁtruncate__mutmut_3(self):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁtruncate__mutmut_4(self):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁtruncate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁtruncate__mutmut_1': xǁDummyFileǁtruncate__mutmut_1, 
        'xǁDummyFileǁtruncate__mutmut_2': xǁDummyFileǁtruncate__mutmut_2, 
        'xǁDummyFileǁtruncate__mutmut_3': xǁDummyFileǁtruncate__mutmut_3, 
        'xǁDummyFileǁtruncate__mutmut_4': xǁDummyFileǁtruncate__mutmut_4
    }
    
    def truncate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁtruncate__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁtruncate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    truncate.__signature__ = _mutmut_signature(xǁDummyFileǁtruncate__mutmut_orig)
    xǁDummyFileǁtruncate__mutmut_orig.__name__ = 'xǁDummyFileǁtruncate'

    def xǁDummyFileǁwrite__mutmut_orig(self, string):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁwrite__mutmut_1(self, string):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁwrite__mutmut_2(self, string):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁwrite__mutmut_3(self, string):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁwrite__mutmut_4(self, string):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁwrite__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁwrite__mutmut_1': xǁDummyFileǁwrite__mutmut_1, 
        'xǁDummyFileǁwrite__mutmut_2': xǁDummyFileǁwrite__mutmut_2, 
        'xǁDummyFileǁwrite__mutmut_3': xǁDummyFileǁwrite__mutmut_3, 
        'xǁDummyFileǁwrite__mutmut_4': xǁDummyFileǁwrite__mutmut_4
    }
    
    def write(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁwrite__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁwrite__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write.__signature__ = _mutmut_signature(xǁDummyFileǁwrite__mutmut_orig)
    xǁDummyFileǁwrite__mutmut_orig.__name__ = 'xǁDummyFileǁwrite'

    def xǁDummyFileǁwritelines__mutmut_orig(self, list_of_strings):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁwritelines__mutmut_1(self, list_of_strings):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁwritelines__mutmut_2(self, list_of_strings):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁwritelines__mutmut_3(self, list_of_strings):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁwritelines__mutmut_4(self, list_of_strings):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁwritelines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁwritelines__mutmut_1': xǁDummyFileǁwritelines__mutmut_1, 
        'xǁDummyFileǁwritelines__mutmut_2': xǁDummyFileǁwritelines__mutmut_2, 
        'xǁDummyFileǁwritelines__mutmut_3': xǁDummyFileǁwritelines__mutmut_3, 
        'xǁDummyFileǁwritelines__mutmut_4': xǁDummyFileǁwritelines__mutmut_4
    }
    
    def writelines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁwritelines__mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁwritelines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    writelines.__signature__ = _mutmut_signature(xǁDummyFileǁwritelines__mutmut_orig)
    xǁDummyFileǁwritelines__mutmut_orig.__name__ = 'xǁDummyFileǁwritelines'

    def __next__(self):
        raise StopIteration()

    def xǁDummyFileǁ__enter____mutmut_orig(self):
        if self.closed:
            raise ValueError('I/O operation on a closed file')
        return

    def xǁDummyFileǁ__enter____mutmut_1(self):
        if self.closed:
            raise ValueError(None)
        return

    def xǁDummyFileǁ__enter____mutmut_2(self):
        if self.closed:
            raise ValueError('XXI/O operation on a closed fileXX')
        return

    def xǁDummyFileǁ__enter____mutmut_3(self):
        if self.closed:
            raise ValueError('i/o operation on a closed file')
        return

    def xǁDummyFileǁ__enter____mutmut_4(self):
        if self.closed:
            raise ValueError('I/O OPERATION ON A CLOSED FILE')
        return
    
    xǁDummyFileǁ__enter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDummyFileǁ__enter____mutmut_1': xǁDummyFileǁ__enter____mutmut_1, 
        'xǁDummyFileǁ__enter____mutmut_2': xǁDummyFileǁ__enter____mutmut_2, 
        'xǁDummyFileǁ__enter____mutmut_3': xǁDummyFileǁ__enter____mutmut_3, 
        'xǁDummyFileǁ__enter____mutmut_4': xǁDummyFileǁ__enter____mutmut_4
    }
    
    def __enter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDummyFileǁ__enter____mutmut_orig"), object.__getattribute__(self, "xǁDummyFileǁ__enter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __enter__.__signature__ = _mutmut_signature(xǁDummyFileǁ__enter____mutmut_orig)
    xǁDummyFileǁ__enter____mutmut_orig.__name__ = 'xǁDummyFileǁ__enter__'

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


def x_rotate_file__mutmut_orig(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_1(filename, *, keep: int = 6):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_2(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep <= 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_3(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 2:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_4(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(None)
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_5(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_6(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(None):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_7(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_8(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(None):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_9(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(None)

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_10(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = None
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_11(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(None)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_12(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = None
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_13(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(None, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_14(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, None):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_15(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_16(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, ):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_17(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(2, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_18(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep - 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_19(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 2):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_20(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(None)
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_21(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(None)

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_22(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = None
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_23(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] - kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_24(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(None):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_25(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(None)):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_26(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(None, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_27(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, None))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_28(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_29(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, ))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_30(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[2:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_31(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_32(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(None):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_33(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            break
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_34(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(None, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_35(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, None)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_36(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_37(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, )

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_38(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(None):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_39(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[+1]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_40(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-2]):
        os.remove(kept_names[-1])

    return


def x_rotate_file__mutmut_41(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(None)

    return


def x_rotate_file__mutmut_42(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[+1])

    return


def x_rotate_file__mutmut_43(filename, *, keep: int = 5):
    """
    If *filename.ext* exists, it will be moved to *filename.1.ext*, 
    with all conflicting filenames being moved up by one, dropping any files beyond *keep*.

    After rotation, *filename* will be available for creation as a new file.

    Fails if *filename* is not a file or if *keep* is not > 0.
    """
    if keep < 1:
        raise ValueError(f'expected "keep" to be >=1, not {keep}')
    if not os.path.exists(filename):
        return
    if not os.path.isfile(filename):
        raise ValueError(f'expected {filename} to be a file')

    fn_root, fn_ext = os.path.splitext(filename)
    kept_names = []
    for i in range(1, keep + 1):
        if fn_ext:
            kept_names.append(f'{fn_root}.{i}{fn_ext}')
        else:
            kept_names.append(f'{fn_root}.{i}')

    fns = [filename] + kept_names
    for orig_name, kept_name in reversed(list(zip(fns, fns[1:]))):
        if not os.path.exists(orig_name):
            continue
        os.rename(orig_name, kept_name)

    if os.path.exists(kept_names[-1]):
        os.remove(kept_names[-2])

    return

x_rotate_file__mutmut_mutants : ClassVar[MutantDict] = {
'x_rotate_file__mutmut_1': x_rotate_file__mutmut_1, 
    'x_rotate_file__mutmut_2': x_rotate_file__mutmut_2, 
    'x_rotate_file__mutmut_3': x_rotate_file__mutmut_3, 
    'x_rotate_file__mutmut_4': x_rotate_file__mutmut_4, 
    'x_rotate_file__mutmut_5': x_rotate_file__mutmut_5, 
    'x_rotate_file__mutmut_6': x_rotate_file__mutmut_6, 
    'x_rotate_file__mutmut_7': x_rotate_file__mutmut_7, 
    'x_rotate_file__mutmut_8': x_rotate_file__mutmut_8, 
    'x_rotate_file__mutmut_9': x_rotate_file__mutmut_9, 
    'x_rotate_file__mutmut_10': x_rotate_file__mutmut_10, 
    'x_rotate_file__mutmut_11': x_rotate_file__mutmut_11, 
    'x_rotate_file__mutmut_12': x_rotate_file__mutmut_12, 
    'x_rotate_file__mutmut_13': x_rotate_file__mutmut_13, 
    'x_rotate_file__mutmut_14': x_rotate_file__mutmut_14, 
    'x_rotate_file__mutmut_15': x_rotate_file__mutmut_15, 
    'x_rotate_file__mutmut_16': x_rotate_file__mutmut_16, 
    'x_rotate_file__mutmut_17': x_rotate_file__mutmut_17, 
    'x_rotate_file__mutmut_18': x_rotate_file__mutmut_18, 
    'x_rotate_file__mutmut_19': x_rotate_file__mutmut_19, 
    'x_rotate_file__mutmut_20': x_rotate_file__mutmut_20, 
    'x_rotate_file__mutmut_21': x_rotate_file__mutmut_21, 
    'x_rotate_file__mutmut_22': x_rotate_file__mutmut_22, 
    'x_rotate_file__mutmut_23': x_rotate_file__mutmut_23, 
    'x_rotate_file__mutmut_24': x_rotate_file__mutmut_24, 
    'x_rotate_file__mutmut_25': x_rotate_file__mutmut_25, 
    'x_rotate_file__mutmut_26': x_rotate_file__mutmut_26, 
    'x_rotate_file__mutmut_27': x_rotate_file__mutmut_27, 
    'x_rotate_file__mutmut_28': x_rotate_file__mutmut_28, 
    'x_rotate_file__mutmut_29': x_rotate_file__mutmut_29, 
    'x_rotate_file__mutmut_30': x_rotate_file__mutmut_30, 
    'x_rotate_file__mutmut_31': x_rotate_file__mutmut_31, 
    'x_rotate_file__mutmut_32': x_rotate_file__mutmut_32, 
    'x_rotate_file__mutmut_33': x_rotate_file__mutmut_33, 
    'x_rotate_file__mutmut_34': x_rotate_file__mutmut_34, 
    'x_rotate_file__mutmut_35': x_rotate_file__mutmut_35, 
    'x_rotate_file__mutmut_36': x_rotate_file__mutmut_36, 
    'x_rotate_file__mutmut_37': x_rotate_file__mutmut_37, 
    'x_rotate_file__mutmut_38': x_rotate_file__mutmut_38, 
    'x_rotate_file__mutmut_39': x_rotate_file__mutmut_39, 
    'x_rotate_file__mutmut_40': x_rotate_file__mutmut_40, 
    'x_rotate_file__mutmut_41': x_rotate_file__mutmut_41, 
    'x_rotate_file__mutmut_42': x_rotate_file__mutmut_42, 
    'x_rotate_file__mutmut_43': x_rotate_file__mutmut_43
}

def rotate_file(*args, **kwargs):
    result = _mutmut_trampoline(x_rotate_file__mutmut_orig, x_rotate_file__mutmut_mutants, args, kwargs)
    return result 

rotate_file.__signature__ = _mutmut_signature(x_rotate_file__mutmut_orig)
x_rotate_file__mutmut_orig.__name__ = 'x_rotate_file'
