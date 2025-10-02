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

"""``jsonutils`` aims to provide various helpers for working with
JSON. Currently it focuses on providing a reliable and intuitive means
of working with `JSON Lines`_-formatted files.

.. _JSON Lines: http://jsonlines.org/

"""


import io
import os
import json


DEFAULT_BLOCKSIZE = 4096


__all__ = ['JSONLIterator', 'reverse_iter_lines']
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


def x_reverse_iter_lines__mutmut_orig(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_1(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=False, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_2(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = None
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_3(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding and file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_4(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = ""
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_5(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = None

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_6(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'XXutf-8XX'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_7(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'UTF-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_8(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = None
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_9(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = None
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_10(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = None

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_11(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'XXXX', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_12(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_13(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_14(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'XX\nXX', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_15(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_16(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_17(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', 'XXXX'

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_18(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(None, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_19(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, None)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_20(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_21(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, )
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_22(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(1, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_23(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = None
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_24(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = None
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_25(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 1 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_26(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 <= cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_27(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = None
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_28(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(None, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_29(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, None)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_30(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_31(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, )
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_32(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos = read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_33(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos += read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_34(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(None, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_35(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, None)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_36(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_37(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, )
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_38(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = None
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_39(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(None)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_40(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = None
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_41(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur - buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_42(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = None

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_43(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 and lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_44(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) <= 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_45(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 3 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_46(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[1] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_47(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] != empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_48(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            break
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_49(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[+1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_50(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-2:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_51(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] != newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_52(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:1:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_53(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:+1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_54(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-2]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_55(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(None) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_56(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = None
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_57(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[1]
    if buff:
        yield buff.decode(encoding) if encoding else buff


def x_reverse_iter_lines__mutmut_58(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object after being passed. Files can be opened in bytes or
            text mode.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    try:
        encoding = encoding or file_obj.encoding
    except AttributeError:
        # BytesIO
        encoding = None
    else:
        encoding = 'utf-8'

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.detach()
    except (AttributeError, io.UnsupportedOperation):
        pass

    empty_bytes, newline_bytes, empty_text = b'', b'\n', ''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    buff = empty_bytes
    cur_pos = file_obj.tell()
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        buff = cur + buff
        lines = buff.splitlines()

        if len(lines) < 2 or lines[0] == empty_bytes:
            continue
        if buff[-1:] == newline_bytes:
            yield empty_text if encoding else empty_bytes
        for line in lines[:0:-1]:
            yield line.decode(encoding) if encoding else line
        buff = lines[0]
    if buff:
        yield buff.decode(None) if encoding else buff

x_reverse_iter_lines__mutmut_mutants : ClassVar[MutantDict] = {
'x_reverse_iter_lines__mutmut_1': x_reverse_iter_lines__mutmut_1, 
    'x_reverse_iter_lines__mutmut_2': x_reverse_iter_lines__mutmut_2, 
    'x_reverse_iter_lines__mutmut_3': x_reverse_iter_lines__mutmut_3, 
    'x_reverse_iter_lines__mutmut_4': x_reverse_iter_lines__mutmut_4, 
    'x_reverse_iter_lines__mutmut_5': x_reverse_iter_lines__mutmut_5, 
    'x_reverse_iter_lines__mutmut_6': x_reverse_iter_lines__mutmut_6, 
    'x_reverse_iter_lines__mutmut_7': x_reverse_iter_lines__mutmut_7, 
    'x_reverse_iter_lines__mutmut_8': x_reverse_iter_lines__mutmut_8, 
    'x_reverse_iter_lines__mutmut_9': x_reverse_iter_lines__mutmut_9, 
    'x_reverse_iter_lines__mutmut_10': x_reverse_iter_lines__mutmut_10, 
    'x_reverse_iter_lines__mutmut_11': x_reverse_iter_lines__mutmut_11, 
    'x_reverse_iter_lines__mutmut_12': x_reverse_iter_lines__mutmut_12, 
    'x_reverse_iter_lines__mutmut_13': x_reverse_iter_lines__mutmut_13, 
    'x_reverse_iter_lines__mutmut_14': x_reverse_iter_lines__mutmut_14, 
    'x_reverse_iter_lines__mutmut_15': x_reverse_iter_lines__mutmut_15, 
    'x_reverse_iter_lines__mutmut_16': x_reverse_iter_lines__mutmut_16, 
    'x_reverse_iter_lines__mutmut_17': x_reverse_iter_lines__mutmut_17, 
    'x_reverse_iter_lines__mutmut_18': x_reverse_iter_lines__mutmut_18, 
    'x_reverse_iter_lines__mutmut_19': x_reverse_iter_lines__mutmut_19, 
    'x_reverse_iter_lines__mutmut_20': x_reverse_iter_lines__mutmut_20, 
    'x_reverse_iter_lines__mutmut_21': x_reverse_iter_lines__mutmut_21, 
    'x_reverse_iter_lines__mutmut_22': x_reverse_iter_lines__mutmut_22, 
    'x_reverse_iter_lines__mutmut_23': x_reverse_iter_lines__mutmut_23, 
    'x_reverse_iter_lines__mutmut_24': x_reverse_iter_lines__mutmut_24, 
    'x_reverse_iter_lines__mutmut_25': x_reverse_iter_lines__mutmut_25, 
    'x_reverse_iter_lines__mutmut_26': x_reverse_iter_lines__mutmut_26, 
    'x_reverse_iter_lines__mutmut_27': x_reverse_iter_lines__mutmut_27, 
    'x_reverse_iter_lines__mutmut_28': x_reverse_iter_lines__mutmut_28, 
    'x_reverse_iter_lines__mutmut_29': x_reverse_iter_lines__mutmut_29, 
    'x_reverse_iter_lines__mutmut_30': x_reverse_iter_lines__mutmut_30, 
    'x_reverse_iter_lines__mutmut_31': x_reverse_iter_lines__mutmut_31, 
    'x_reverse_iter_lines__mutmut_32': x_reverse_iter_lines__mutmut_32, 
    'x_reverse_iter_lines__mutmut_33': x_reverse_iter_lines__mutmut_33, 
    'x_reverse_iter_lines__mutmut_34': x_reverse_iter_lines__mutmut_34, 
    'x_reverse_iter_lines__mutmut_35': x_reverse_iter_lines__mutmut_35, 
    'x_reverse_iter_lines__mutmut_36': x_reverse_iter_lines__mutmut_36, 
    'x_reverse_iter_lines__mutmut_37': x_reverse_iter_lines__mutmut_37, 
    'x_reverse_iter_lines__mutmut_38': x_reverse_iter_lines__mutmut_38, 
    'x_reverse_iter_lines__mutmut_39': x_reverse_iter_lines__mutmut_39, 
    'x_reverse_iter_lines__mutmut_40': x_reverse_iter_lines__mutmut_40, 
    'x_reverse_iter_lines__mutmut_41': x_reverse_iter_lines__mutmut_41, 
    'x_reverse_iter_lines__mutmut_42': x_reverse_iter_lines__mutmut_42, 
    'x_reverse_iter_lines__mutmut_43': x_reverse_iter_lines__mutmut_43, 
    'x_reverse_iter_lines__mutmut_44': x_reverse_iter_lines__mutmut_44, 
    'x_reverse_iter_lines__mutmut_45': x_reverse_iter_lines__mutmut_45, 
    'x_reverse_iter_lines__mutmut_46': x_reverse_iter_lines__mutmut_46, 
    'x_reverse_iter_lines__mutmut_47': x_reverse_iter_lines__mutmut_47, 
    'x_reverse_iter_lines__mutmut_48': x_reverse_iter_lines__mutmut_48, 
    'x_reverse_iter_lines__mutmut_49': x_reverse_iter_lines__mutmut_49, 
    'x_reverse_iter_lines__mutmut_50': x_reverse_iter_lines__mutmut_50, 
    'x_reverse_iter_lines__mutmut_51': x_reverse_iter_lines__mutmut_51, 
    'x_reverse_iter_lines__mutmut_52': x_reverse_iter_lines__mutmut_52, 
    'x_reverse_iter_lines__mutmut_53': x_reverse_iter_lines__mutmut_53, 
    'x_reverse_iter_lines__mutmut_54': x_reverse_iter_lines__mutmut_54, 
    'x_reverse_iter_lines__mutmut_55': x_reverse_iter_lines__mutmut_55, 
    'x_reverse_iter_lines__mutmut_56': x_reverse_iter_lines__mutmut_56, 
    'x_reverse_iter_lines__mutmut_57': x_reverse_iter_lines__mutmut_57, 
    'x_reverse_iter_lines__mutmut_58': x_reverse_iter_lines__mutmut_58
}

def reverse_iter_lines(*args, **kwargs):
    result = _mutmut_trampoline(x_reverse_iter_lines__mutmut_orig, x_reverse_iter_lines__mutmut_mutants, args, kwargs)
    return result 

reverse_iter_lines.__signature__ = _mutmut_signature(x_reverse_iter_lines__mutmut_orig)
x_reverse_iter_lines__mutmut_orig.__name__ = 'x_reverse_iter_lines'



"""
TODO: allow passthroughs for:

json.load(fp[, encoding[, cls[, object_hook[, parse_float[, parse_int[, parse_constant[, object_pairs_hook[, **kw]]]]]]]])
"""


class JSONLIterator:
    """The ``JSONLIterator`` is used to iterate over JSON-encoded objects
    stored in the `JSON Lines format`_ (one object per line).

    Most notably it has the ability to efficiently read from the
    bottom of files, making it very effective for reading in simple
    append-only JSONL use cases. It also has the ability to start from
    anywhere in the file and ignore corrupted lines.

    Args:
        file_obj (file): An open file object.
        ignore_errors (bool): Whether to skip over lines that raise an error on
            deserialization (:func:`json.loads`).
        reverse (bool): Controls the direction of the iteration.
            Defaults to ``False``. If set to ``True`` and *rel_seek*
            is unset, seeks to the end of the file before iteration
            begins.
        rel_seek (float): Used to preseek the start position of
            iteration. Set to 0.0 for the start of the file, 1.0 for the
            end, and anything in between.

    .. _JSON Lines format: http://jsonlines.org/
    """
    def xǁJSONLIteratorǁ__init____mutmut_orig(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_1(self, file_obj,
                 ignore_errors=True, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_2(self, file_obj,
                 ignore_errors=False, reverse=True, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_3(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = None
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_4(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(None)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_5(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = None
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_6(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = None

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_7(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is not None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_8(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = None
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_9(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 2.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_10(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_11(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not +1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_12(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -2.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_13(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 <= rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_14(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek <= 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_15(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 2.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_16(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError(None)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_17(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" / rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_18(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("XX'rel_seek' expected a float betweenXX"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_19(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'REL_SEEK' EXPECTED A FLOAT BETWEEN"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_20(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             "XX -1.0 and 1.0, not %rXX" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_21(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 AND 1.0, NOT %R" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_22(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek <= 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_23(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 1:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_24(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = None
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_25(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 + rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_26(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 2.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_27(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = None
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_28(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = None
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_29(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4097
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_30(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_31(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = None
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_32(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(None,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_33(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=None,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_34(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=None)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_35(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_36(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_37(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 )
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_38(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=True)
        else:
            self._line_iter = iter(self._file_obj)
    def xǁJSONLIteratorǁ__init____mutmut_39(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = None
    def xǁJSONLIteratorǁ__init____mutmut_40(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(None)
    
    xǁJSONLIteratorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLIteratorǁ__init____mutmut_1': xǁJSONLIteratorǁ__init____mutmut_1, 
        'xǁJSONLIteratorǁ__init____mutmut_2': xǁJSONLIteratorǁ__init____mutmut_2, 
        'xǁJSONLIteratorǁ__init____mutmut_3': xǁJSONLIteratorǁ__init____mutmut_3, 
        'xǁJSONLIteratorǁ__init____mutmut_4': xǁJSONLIteratorǁ__init____mutmut_4, 
        'xǁJSONLIteratorǁ__init____mutmut_5': xǁJSONLIteratorǁ__init____mutmut_5, 
        'xǁJSONLIteratorǁ__init____mutmut_6': xǁJSONLIteratorǁ__init____mutmut_6, 
        'xǁJSONLIteratorǁ__init____mutmut_7': xǁJSONLIteratorǁ__init____mutmut_7, 
        'xǁJSONLIteratorǁ__init____mutmut_8': xǁJSONLIteratorǁ__init____mutmut_8, 
        'xǁJSONLIteratorǁ__init____mutmut_9': xǁJSONLIteratorǁ__init____mutmut_9, 
        'xǁJSONLIteratorǁ__init____mutmut_10': xǁJSONLIteratorǁ__init____mutmut_10, 
        'xǁJSONLIteratorǁ__init____mutmut_11': xǁJSONLIteratorǁ__init____mutmut_11, 
        'xǁJSONLIteratorǁ__init____mutmut_12': xǁJSONLIteratorǁ__init____mutmut_12, 
        'xǁJSONLIteratorǁ__init____mutmut_13': xǁJSONLIteratorǁ__init____mutmut_13, 
        'xǁJSONLIteratorǁ__init____mutmut_14': xǁJSONLIteratorǁ__init____mutmut_14, 
        'xǁJSONLIteratorǁ__init____mutmut_15': xǁJSONLIteratorǁ__init____mutmut_15, 
        'xǁJSONLIteratorǁ__init____mutmut_16': xǁJSONLIteratorǁ__init____mutmut_16, 
        'xǁJSONLIteratorǁ__init____mutmut_17': xǁJSONLIteratorǁ__init____mutmut_17, 
        'xǁJSONLIteratorǁ__init____mutmut_18': xǁJSONLIteratorǁ__init____mutmut_18, 
        'xǁJSONLIteratorǁ__init____mutmut_19': xǁJSONLIteratorǁ__init____mutmut_19, 
        'xǁJSONLIteratorǁ__init____mutmut_20': xǁJSONLIteratorǁ__init____mutmut_20, 
        'xǁJSONLIteratorǁ__init____mutmut_21': xǁJSONLIteratorǁ__init____mutmut_21, 
        'xǁJSONLIteratorǁ__init____mutmut_22': xǁJSONLIteratorǁ__init____mutmut_22, 
        'xǁJSONLIteratorǁ__init____mutmut_23': xǁJSONLIteratorǁ__init____mutmut_23, 
        'xǁJSONLIteratorǁ__init____mutmut_24': xǁJSONLIteratorǁ__init____mutmut_24, 
        'xǁJSONLIteratorǁ__init____mutmut_25': xǁJSONLIteratorǁ__init____mutmut_25, 
        'xǁJSONLIteratorǁ__init____mutmut_26': xǁJSONLIteratorǁ__init____mutmut_26, 
        'xǁJSONLIteratorǁ__init____mutmut_27': xǁJSONLIteratorǁ__init____mutmut_27, 
        'xǁJSONLIteratorǁ__init____mutmut_28': xǁJSONLIteratorǁ__init____mutmut_28, 
        'xǁJSONLIteratorǁ__init____mutmut_29': xǁJSONLIteratorǁ__init____mutmut_29, 
        'xǁJSONLIteratorǁ__init____mutmut_30': xǁJSONLIteratorǁ__init____mutmut_30, 
        'xǁJSONLIteratorǁ__init____mutmut_31': xǁJSONLIteratorǁ__init____mutmut_31, 
        'xǁJSONLIteratorǁ__init____mutmut_32': xǁJSONLIteratorǁ__init____mutmut_32, 
        'xǁJSONLIteratorǁ__init____mutmut_33': xǁJSONLIteratorǁ__init____mutmut_33, 
        'xǁJSONLIteratorǁ__init____mutmut_34': xǁJSONLIteratorǁ__init____mutmut_34, 
        'xǁJSONLIteratorǁ__init____mutmut_35': xǁJSONLIteratorǁ__init____mutmut_35, 
        'xǁJSONLIteratorǁ__init____mutmut_36': xǁJSONLIteratorǁ__init____mutmut_36, 
        'xǁJSONLIteratorǁ__init____mutmut_37': xǁJSONLIteratorǁ__init____mutmut_37, 
        'xǁJSONLIteratorǁ__init____mutmut_38': xǁJSONLIteratorǁ__init____mutmut_38, 
        'xǁJSONLIteratorǁ__init____mutmut_39': xǁJSONLIteratorǁ__init____mutmut_39, 
        'xǁJSONLIteratorǁ__init____mutmut_40': xǁJSONLIteratorǁ__init____mutmut_40
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLIteratorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁJSONLIteratorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁJSONLIteratorǁ__init____mutmut_orig)
    xǁJSONLIteratorǁ__init____mutmut_orig.__name__ = 'xǁJSONLIteratorǁ__init__'

    @property
    def cur_byte_pos(self):
        "A property representing where in the file the iterator is reading."
        return self._file_obj.tell()

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_orig(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_1(self):
        "XXAligns the file object's position to the next newline.XX"
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_2(self):
        "aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_3(self):
        "ALIGNS THE FILE OBJECT'S POSITION TO THE NEXT NEWLINE."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_4(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = None
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_5(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = None
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_6(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = 'XXXX', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_7(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 1
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_8(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = None
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_9(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while 'XX\nXX' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_10(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_11(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = None
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_12(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(None)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_13(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read = bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_14(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read -= bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_15(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = None
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_16(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read + bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_17(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') - total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_18(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index(None) + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_19(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.rindex('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_20(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('XX\nXX') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_21(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(None)

    def xǁJSONLIteratorǁ_align_to_newline__mutmut_22(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos - newline_offset)
    
    xǁJSONLIteratorǁ_align_to_newline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLIteratorǁ_align_to_newline__mutmut_1': xǁJSONLIteratorǁ_align_to_newline__mutmut_1, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_2': xǁJSONLIteratorǁ_align_to_newline__mutmut_2, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_3': xǁJSONLIteratorǁ_align_to_newline__mutmut_3, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_4': xǁJSONLIteratorǁ_align_to_newline__mutmut_4, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_5': xǁJSONLIteratorǁ_align_to_newline__mutmut_5, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_6': xǁJSONLIteratorǁ_align_to_newline__mutmut_6, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_7': xǁJSONLIteratorǁ_align_to_newline__mutmut_7, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_8': xǁJSONLIteratorǁ_align_to_newline__mutmut_8, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_9': xǁJSONLIteratorǁ_align_to_newline__mutmut_9, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_10': xǁJSONLIteratorǁ_align_to_newline__mutmut_10, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_11': xǁJSONLIteratorǁ_align_to_newline__mutmut_11, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_12': xǁJSONLIteratorǁ_align_to_newline__mutmut_12, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_13': xǁJSONLIteratorǁ_align_to_newline__mutmut_13, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_14': xǁJSONLIteratorǁ_align_to_newline__mutmut_14, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_15': xǁJSONLIteratorǁ_align_to_newline__mutmut_15, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_16': xǁJSONLIteratorǁ_align_to_newline__mutmut_16, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_17': xǁJSONLIteratorǁ_align_to_newline__mutmut_17, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_18': xǁJSONLIteratorǁ_align_to_newline__mutmut_18, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_19': xǁJSONLIteratorǁ_align_to_newline__mutmut_19, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_20': xǁJSONLIteratorǁ_align_to_newline__mutmut_20, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_21': xǁJSONLIteratorǁ_align_to_newline__mutmut_21, 
        'xǁJSONLIteratorǁ_align_to_newline__mutmut_22': xǁJSONLIteratorǁ_align_to_newline__mutmut_22
    }
    
    def _align_to_newline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLIteratorǁ_align_to_newline__mutmut_orig"), object.__getattribute__(self, "xǁJSONLIteratorǁ_align_to_newline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _align_to_newline.__signature__ = _mutmut_signature(xǁJSONLIteratorǁ_align_to_newline__mutmut_orig)
    xǁJSONLIteratorǁ_align_to_newline__mutmut_orig.__name__ = 'xǁJSONLIteratorǁ_align_to_newline'

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_orig(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_1(self):
        "XXSets the file object's position to the relative location set above.XX"
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_2(self):
        "sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_3(self):
        "SETS THE FILE OBJECT'S POSITION TO THE RELATIVE LOCATION SET ABOVE."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_4(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = None
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_5(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs != 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_6(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 1.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_7(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(None, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_8(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, None)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_9(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_10(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, )
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_11(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(1, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_12(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(None, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_13(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, None)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_14(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_15(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, )
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_16(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(1, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_17(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = None
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_18(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs != 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_19(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 2.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_20(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = None
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_21(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = None
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_22(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(None)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_23(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size / rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_24(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(None, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_25(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, None)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_26(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_27(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, )
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def xǁJSONLIteratorǁ_init_rel_seek__mutmut_28(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = None
    
    xǁJSONLIteratorǁ_init_rel_seek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLIteratorǁ_init_rel_seek__mutmut_1': xǁJSONLIteratorǁ_init_rel_seek__mutmut_1, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_2': xǁJSONLIteratorǁ_init_rel_seek__mutmut_2, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_3': xǁJSONLIteratorǁ_init_rel_seek__mutmut_3, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_4': xǁJSONLIteratorǁ_init_rel_seek__mutmut_4, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_5': xǁJSONLIteratorǁ_init_rel_seek__mutmut_5, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_6': xǁJSONLIteratorǁ_init_rel_seek__mutmut_6, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_7': xǁJSONLIteratorǁ_init_rel_seek__mutmut_7, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_8': xǁJSONLIteratorǁ_init_rel_seek__mutmut_8, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_9': xǁJSONLIteratorǁ_init_rel_seek__mutmut_9, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_10': xǁJSONLIteratorǁ_init_rel_seek__mutmut_10, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_11': xǁJSONLIteratorǁ_init_rel_seek__mutmut_11, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_12': xǁJSONLIteratorǁ_init_rel_seek__mutmut_12, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_13': xǁJSONLIteratorǁ_init_rel_seek__mutmut_13, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_14': xǁJSONLIteratorǁ_init_rel_seek__mutmut_14, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_15': xǁJSONLIteratorǁ_init_rel_seek__mutmut_15, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_16': xǁJSONLIteratorǁ_init_rel_seek__mutmut_16, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_17': xǁJSONLIteratorǁ_init_rel_seek__mutmut_17, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_18': xǁJSONLIteratorǁ_init_rel_seek__mutmut_18, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_19': xǁJSONLIteratorǁ_init_rel_seek__mutmut_19, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_20': xǁJSONLIteratorǁ_init_rel_seek__mutmut_20, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_21': xǁJSONLIteratorǁ_init_rel_seek__mutmut_21, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_22': xǁJSONLIteratorǁ_init_rel_seek__mutmut_22, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_23': xǁJSONLIteratorǁ_init_rel_seek__mutmut_23, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_24': xǁJSONLIteratorǁ_init_rel_seek__mutmut_24, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_25': xǁJSONLIteratorǁ_init_rel_seek__mutmut_25, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_26': xǁJSONLIteratorǁ_init_rel_seek__mutmut_26, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_27': xǁJSONLIteratorǁ_init_rel_seek__mutmut_27, 
        'xǁJSONLIteratorǁ_init_rel_seek__mutmut_28': xǁJSONLIteratorǁ_init_rel_seek__mutmut_28
    }
    
    def _init_rel_seek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLIteratorǁ_init_rel_seek__mutmut_orig"), object.__getattribute__(self, "xǁJSONLIteratorǁ_init_rel_seek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _init_rel_seek.__signature__ = _mutmut_signature(xǁJSONLIteratorǁ_init_rel_seek__mutmut_orig)
    xǁJSONLIteratorǁ_init_rel_seek__mutmut_orig.__name__ = 'xǁJSONLIteratorǁ_init_rel_seek'

    def __iter__(self):
        return self

    def xǁJSONLIteratorǁnext__mutmut_orig(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_1(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 2:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_2(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = None
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_3(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).rstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_4(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(None).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_5(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_6(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                break
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_7(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = None
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_8(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(None)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_9(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if self.ignore_errors:
                    raise
                continue
            return obj

    def xǁJSONLIteratorǁnext__mutmut_10(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                break
            return obj
    
    xǁJSONLIteratorǁnext__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLIteratorǁnext__mutmut_1': xǁJSONLIteratorǁnext__mutmut_1, 
        'xǁJSONLIteratorǁnext__mutmut_2': xǁJSONLIteratorǁnext__mutmut_2, 
        'xǁJSONLIteratorǁnext__mutmut_3': xǁJSONLIteratorǁnext__mutmut_3, 
        'xǁJSONLIteratorǁnext__mutmut_4': xǁJSONLIteratorǁnext__mutmut_4, 
        'xǁJSONLIteratorǁnext__mutmut_5': xǁJSONLIteratorǁnext__mutmut_5, 
        'xǁJSONLIteratorǁnext__mutmut_6': xǁJSONLIteratorǁnext__mutmut_6, 
        'xǁJSONLIteratorǁnext__mutmut_7': xǁJSONLIteratorǁnext__mutmut_7, 
        'xǁJSONLIteratorǁnext__mutmut_8': xǁJSONLIteratorǁnext__mutmut_8, 
        'xǁJSONLIteratorǁnext__mutmut_9': xǁJSONLIteratorǁnext__mutmut_9, 
        'xǁJSONLIteratorǁnext__mutmut_10': xǁJSONLIteratorǁnext__mutmut_10
    }
    
    def next(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLIteratorǁnext__mutmut_orig"), object.__getattribute__(self, "xǁJSONLIteratorǁnext__mutmut_mutants"), args, kwargs, self)
        return result 
    
    next.__signature__ = _mutmut_signature(xǁJSONLIteratorǁnext__mutmut_orig)
    xǁJSONLIteratorǁnext__mutmut_orig.__name__ = 'xǁJSONLIteratorǁnext'

    __next__ = next


if __name__ == '__main__':
    def _main():
        import sys
        if '-h' in sys.argv or '--help' in sys.argv:
            print('loads one or more JSON Line files for basic validation.')
            return
        verbose = False
        if '-v' in sys.argv or '--verbose' in sys.argv:
            verbose = True
        file_count, obj_count = 0, 0
        filenames = sys.argv[1:]
        for filename in filenames:
            if filename in ('-h', '--help', '-v', '--verbose'):
                continue
            file_count += 1
            with open(filename, 'rb') as file_obj:
                iterator = JSONLIterator(file_obj)
                cur_obj_count = 0
                while 1:
                    try:
                        next(iterator)
                    except ValueError:
                        print('error reading object #%s around byte %s in %s'
                              % (cur_obj_count + 1, iterator.cur_byte_pos, filename))
                        return
                    except StopIteration:
                        break
                    obj_count += 1
                    cur_obj_count += 1
                    if verbose and obj_count and obj_count % 100 == 0:
                        sys.stdout.write('.')
                        if obj_count % 10000:
                            sys.stdout.write('%s\n' % obj_count)
        if verbose:
            print('files checked: %s' % file_count)
            print('objects loaded: %s' % obj_count)
        return

    _main()
