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

"""At its heart, Python can be viewed as an extension of the C
programming language. Springing from the most popular systems
programming language has made Python itself a great language for
systems programming. One key to success in this domain is Python's
very serviceable :mod:`socket` module and its :class:`socket.socket`
type.

The ``socketutils`` module provides natural next steps to the ``socket``
builtin: straightforward, tested building blocks for higher-level
protocols.

The :class:`BufferedSocket` wraps an ordinary socket, providing a
layer of intuitive buffering for both sending and receiving. This
facilitates parsing messages from streams, i.e., all sockets with type
``SOCK_STREAM``. The BufferedSocket enables receiving until the next
relevant token, up to a certain size, or until the connection is
closed. For all of these, it provides consistent APIs to size
limiting, as well as timeouts that are compatible with multiple
concurrency paradigms. Use it to parse the next one-off text or binary
socket protocol you encounter.

This module also provides the :class:`NetstringSocket`, a pure-Python
implementation of `the Netstring protocol`_, built on top of the
:class:`BufferedSocket`, serving as a ready-made, production-grade example.

Special thanks to `Kurt Rose`_ for his original authorship and all his
contributions on this module. Also thanks to `Daniel J. Bernstein`_, the
original author of `Netstring`_.

.. _the Netstring protocol: https://en.wikipedia.org/wiki/Netstring
.. _Kurt Rose: https://github.com/doublereedkurt
.. _Daniel J. Bernstein: https://cr.yp.to/
.. _Netstring: https://cr.yp.to/proto/netstrings.txt

"""

import time
import socket

try:
    from threading import RLock
except Exception:
    class RLock:
        'Dummy reentrant lock for builds without threads'
        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass


_UNSET = object()


DEFAULT_TIMEOUT = 10  # 10 seconds
DEFAULT_MAXSIZE = 32 * 1024  # 32kb
_RECV_LARGE_MAXSIZE = 1024 ** 5  # 1PB
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


class BufferedSocket:
    """Mainly provides recv_until and recv_size. recv, send, sendall, and
    peek all function as similarly as possible to the built-in socket
    API.

    This type has been tested against both the built-in socket type as
    well as those from gevent and eventlet. It also features support
    for sockets with timeouts set to 0 (aka nonblocking), provided the
    caller is prepared to handle the EWOULDBLOCK exceptions.

    Args:
        sock (socket): The connected socket to be wrapped.
        timeout (float): The default timeout for sends and recvs, in
            seconds. Set to ``None`` for no timeout, and 0 for
            nonblocking. Defaults to *sock*'s own timeout if already set,
            and 10 seconds otherwise.
        maxsize (int): The default maximum number of bytes to be received
            into the buffer before it is considered full and raises an
            exception. Defaults to 32 kilobytes.
        recvsize (int): The number of bytes to recv for every
            lower-level :meth:`socket.recv` call. Defaults to *maxsize*.

    *timeout* and *maxsize* can both be overridden on individual socket
    operations.

    All ``recv`` methods return bytestrings (:class:`bytes`) and can
    raise :exc:`socket.error`. :exc:`Timeout`,
    :exc:`ConnectionClosed`, and :exc:`MessageTooLong` all inherit
    from :exc:`socket.error` and exist to provide better error
    messages. Received bytes are always buffered, even if an exception
    is raised. Use :meth:`BufferedSocket.getrecvbuffer` to retrieve
    partial recvs.

    BufferedSocket does not replace the built-in socket by any
    means. While the overlapping parts of the API are kept parallel to
    the built-in :class:`socket.socket`, BufferedSocket does not
    inherit from socket, and most socket functionality is only
    available on the underlying socket. :meth:`socket.getpeername`,
    :meth:`socket.getsockname`, :meth:`socket.fileno`, and others are
    only available on the underlying socket that is wrapped. Use the
    ``BufferedSocket.sock`` attribute to access it. See the examples
    for more information on how to use BufferedSockets with built-in
    sockets.

    The BufferedSocket is threadsafe, but consider the semantics of
    your protocol before accessing a single socket from multiple
    threads. Similarly, once the BufferedSocket is constructed, avoid
    using the underlying socket directly. Only use it for operations
    unrelated to messages, e.g., :meth:`socket.getpeername`.

    """
    def xǁBufferedSocketǁ__init____mutmut_orig(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_1(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = None
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_2(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = None
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_3(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b'XXXX'
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_4(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_5(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_6(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = None
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_7(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = None

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_8(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(None)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_9(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is not _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_10(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is not None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_11(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = None
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_12(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = None
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_13(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is not None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_14(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = None
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_15(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = None

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_16(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(None)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_17(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is not _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_18(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = None
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_19(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = None

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_20(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(None)

        self._send_lock = RLock()
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_21(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = None
        self._recv_lock = RLock()
    def xǁBufferedSocketǁ__init____mutmut_22(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self._send_lock = RLock()
        self._recv_lock = None
    
    xǁBufferedSocketǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁ__init____mutmut_1': xǁBufferedSocketǁ__init____mutmut_1, 
        'xǁBufferedSocketǁ__init____mutmut_2': xǁBufferedSocketǁ__init____mutmut_2, 
        'xǁBufferedSocketǁ__init____mutmut_3': xǁBufferedSocketǁ__init____mutmut_3, 
        'xǁBufferedSocketǁ__init____mutmut_4': xǁBufferedSocketǁ__init____mutmut_4, 
        'xǁBufferedSocketǁ__init____mutmut_5': xǁBufferedSocketǁ__init____mutmut_5, 
        'xǁBufferedSocketǁ__init____mutmut_6': xǁBufferedSocketǁ__init____mutmut_6, 
        'xǁBufferedSocketǁ__init____mutmut_7': xǁBufferedSocketǁ__init____mutmut_7, 
        'xǁBufferedSocketǁ__init____mutmut_8': xǁBufferedSocketǁ__init____mutmut_8, 
        'xǁBufferedSocketǁ__init____mutmut_9': xǁBufferedSocketǁ__init____mutmut_9, 
        'xǁBufferedSocketǁ__init____mutmut_10': xǁBufferedSocketǁ__init____mutmut_10, 
        'xǁBufferedSocketǁ__init____mutmut_11': xǁBufferedSocketǁ__init____mutmut_11, 
        'xǁBufferedSocketǁ__init____mutmut_12': xǁBufferedSocketǁ__init____mutmut_12, 
        'xǁBufferedSocketǁ__init____mutmut_13': xǁBufferedSocketǁ__init____mutmut_13, 
        'xǁBufferedSocketǁ__init____mutmut_14': xǁBufferedSocketǁ__init____mutmut_14, 
        'xǁBufferedSocketǁ__init____mutmut_15': xǁBufferedSocketǁ__init____mutmut_15, 
        'xǁBufferedSocketǁ__init____mutmut_16': xǁBufferedSocketǁ__init____mutmut_16, 
        'xǁBufferedSocketǁ__init____mutmut_17': xǁBufferedSocketǁ__init____mutmut_17, 
        'xǁBufferedSocketǁ__init____mutmut_18': xǁBufferedSocketǁ__init____mutmut_18, 
        'xǁBufferedSocketǁ__init____mutmut_19': xǁBufferedSocketǁ__init____mutmut_19, 
        'xǁBufferedSocketǁ__init____mutmut_20': xǁBufferedSocketǁ__init____mutmut_20, 
        'xǁBufferedSocketǁ__init____mutmut_21': xǁBufferedSocketǁ__init____mutmut_21, 
        'xǁBufferedSocketǁ__init____mutmut_22': xǁBufferedSocketǁ__init____mutmut_22
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBufferedSocketǁ__init____mutmut_orig)
    xǁBufferedSocketǁ__init____mutmut_orig.__name__ = 'xǁBufferedSocketǁ__init__'

    def xǁBufferedSocketǁsettimeout__mutmut_orig(self, timeout):
        "Set the default *timeout* for future operations, in seconds."
        self.timeout = timeout

    def xǁBufferedSocketǁsettimeout__mutmut_1(self, timeout):
        "XXSet the default *timeout* for future operations, in seconds.XX"
        self.timeout = timeout

    def xǁBufferedSocketǁsettimeout__mutmut_2(self, timeout):
        "set the default *timeout* for future operations, in seconds."
        self.timeout = timeout

    def xǁBufferedSocketǁsettimeout__mutmut_3(self, timeout):
        "SET THE DEFAULT *TIMEOUT* FOR FUTURE OPERATIONS, IN SECONDS."
        self.timeout = timeout

    def xǁBufferedSocketǁsettimeout__mutmut_4(self, timeout):
        "Set the default *timeout* for future operations, in seconds."
        self.timeout = None
    
    xǁBufferedSocketǁsettimeout__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsettimeout__mutmut_1': xǁBufferedSocketǁsettimeout__mutmut_1, 
        'xǁBufferedSocketǁsettimeout__mutmut_2': xǁBufferedSocketǁsettimeout__mutmut_2, 
        'xǁBufferedSocketǁsettimeout__mutmut_3': xǁBufferedSocketǁsettimeout__mutmut_3, 
        'xǁBufferedSocketǁsettimeout__mutmut_4': xǁBufferedSocketǁsettimeout__mutmut_4
    }
    
    def settimeout(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsettimeout__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsettimeout__mutmut_mutants"), args, kwargs, self)
        return result 
    
    settimeout.__signature__ = _mutmut_signature(xǁBufferedSocketǁsettimeout__mutmut_orig)
    xǁBufferedSocketǁsettimeout__mutmut_orig.__name__ = 'xǁBufferedSocketǁsettimeout'

    def gettimeout(self):
        return self.timeout

    def xǁBufferedSocketǁsetblocking__mutmut_orig(self, blocking):
        self.timeout = None if blocking else 0.0

    def xǁBufferedSocketǁsetblocking__mutmut_1(self, blocking):
        self.timeout = None

    def xǁBufferedSocketǁsetblocking__mutmut_2(self, blocking):
        self.timeout = None if blocking else 1.0
    
    xǁBufferedSocketǁsetblocking__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsetblocking__mutmut_1': xǁBufferedSocketǁsetblocking__mutmut_1, 
        'xǁBufferedSocketǁsetblocking__mutmut_2': xǁBufferedSocketǁsetblocking__mutmut_2
    }
    
    def setblocking(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsetblocking__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsetblocking__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setblocking.__signature__ = _mutmut_signature(xǁBufferedSocketǁsetblocking__mutmut_orig)
    xǁBufferedSocketǁsetblocking__mutmut_orig.__name__ = 'xǁBufferedSocketǁsetblocking'

    def xǁBufferedSocketǁsetmaxsize__mutmut_orig(self, maxsize):
        """Set the default maximum buffer size *maxsize* for future
        operations, in bytes. Does not truncate the current buffer.
        """
        self.maxsize = maxsize

    def xǁBufferedSocketǁsetmaxsize__mutmut_1(self, maxsize):
        """Set the default maximum buffer size *maxsize* for future
        operations, in bytes. Does not truncate the current buffer.
        """
        self.maxsize = None
    
    xǁBufferedSocketǁsetmaxsize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsetmaxsize__mutmut_1': xǁBufferedSocketǁsetmaxsize__mutmut_1
    }
    
    def setmaxsize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsetmaxsize__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsetmaxsize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setmaxsize.__signature__ = _mutmut_signature(xǁBufferedSocketǁsetmaxsize__mutmut_orig)
    xǁBufferedSocketǁsetmaxsize__mutmut_orig.__name__ = 'xǁBufferedSocketǁsetmaxsize'

    def xǁBufferedSocketǁgetrecvbuffer__mutmut_orig(self):
        "Returns the receive buffer bytestring (rbuf)."
        with self._recv_lock:
            return self.rbuf

    def xǁBufferedSocketǁgetrecvbuffer__mutmut_1(self):
        "XXReturns the receive buffer bytestring (rbuf).XX"
        with self._recv_lock:
            return self.rbuf

    def xǁBufferedSocketǁgetrecvbuffer__mutmut_2(self):
        "returns the receive buffer bytestring (rbuf)."
        with self._recv_lock:
            return self.rbuf

    def xǁBufferedSocketǁgetrecvbuffer__mutmut_3(self):
        "RETURNS THE RECEIVE BUFFER BYTESTRING (RBUF)."
        with self._recv_lock:
            return self.rbuf
    
    xǁBufferedSocketǁgetrecvbuffer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁgetrecvbuffer__mutmut_1': xǁBufferedSocketǁgetrecvbuffer__mutmut_1, 
        'xǁBufferedSocketǁgetrecvbuffer__mutmut_2': xǁBufferedSocketǁgetrecvbuffer__mutmut_2, 
        'xǁBufferedSocketǁgetrecvbuffer__mutmut_3': xǁBufferedSocketǁgetrecvbuffer__mutmut_3
    }
    
    def getrecvbuffer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁgetrecvbuffer__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁgetrecvbuffer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    getrecvbuffer.__signature__ = _mutmut_signature(xǁBufferedSocketǁgetrecvbuffer__mutmut_orig)
    xǁBufferedSocketǁgetrecvbuffer__mutmut_orig.__name__ = 'xǁBufferedSocketǁgetrecvbuffer'

    def xǁBufferedSocketǁgetsendbuffer__mutmut_orig(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_1(self):
        "XXReturns a copy of the send buffer list.XX"
        with self._send_lock:
            return b''.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_2(self):
        "returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_3(self):
        "RETURNS A COPY OF THE SEND BUFFER LIST."
        with self._send_lock:
            return b''.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_4(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(None)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_5(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b'XXXX'.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_6(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(self.sbuf)

    def xǁBufferedSocketǁgetsendbuffer__mutmut_7(self):
        "Returns a copy of the send buffer list."
        with self._send_lock:
            return b''.join(self.sbuf)
    
    xǁBufferedSocketǁgetsendbuffer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁgetsendbuffer__mutmut_1': xǁBufferedSocketǁgetsendbuffer__mutmut_1, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_2': xǁBufferedSocketǁgetsendbuffer__mutmut_2, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_3': xǁBufferedSocketǁgetsendbuffer__mutmut_3, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_4': xǁBufferedSocketǁgetsendbuffer__mutmut_4, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_5': xǁBufferedSocketǁgetsendbuffer__mutmut_5, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_6': xǁBufferedSocketǁgetsendbuffer__mutmut_6, 
        'xǁBufferedSocketǁgetsendbuffer__mutmut_7': xǁBufferedSocketǁgetsendbuffer__mutmut_7
    }
    
    def getsendbuffer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁgetsendbuffer__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁgetsendbuffer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    getsendbuffer.__signature__ = _mutmut_signature(xǁBufferedSocketǁgetsendbuffer__mutmut_orig)
    xǁBufferedSocketǁgetsendbuffer__mutmut_orig.__name__ = 'xǁBufferedSocketǁgetsendbuffer'

    def xǁBufferedSocketǁrecv__mutmut_orig(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_1(self, size, flags=1, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_2(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is not _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_3(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = None
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_4(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError(None)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_5(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" / flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_6(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("XXnon-zero flags not supported: %rXX" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_7(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("NON-ZERO FLAGS NOT SUPPORTED: %R" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_8(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) > size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_9(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = None
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_10(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = None
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_11(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b'XXXX'
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_12(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_13(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_14(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(None)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_15(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = None
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_16(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(None)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_17(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(None)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_18(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) >= size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def xǁBufferedSocketǁrecv__mutmut_19(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = None
        return data
    
    xǁBufferedSocketǁrecv__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁrecv__mutmut_1': xǁBufferedSocketǁrecv__mutmut_1, 
        'xǁBufferedSocketǁrecv__mutmut_2': xǁBufferedSocketǁrecv__mutmut_2, 
        'xǁBufferedSocketǁrecv__mutmut_3': xǁBufferedSocketǁrecv__mutmut_3, 
        'xǁBufferedSocketǁrecv__mutmut_4': xǁBufferedSocketǁrecv__mutmut_4, 
        'xǁBufferedSocketǁrecv__mutmut_5': xǁBufferedSocketǁrecv__mutmut_5, 
        'xǁBufferedSocketǁrecv__mutmut_6': xǁBufferedSocketǁrecv__mutmut_6, 
        'xǁBufferedSocketǁrecv__mutmut_7': xǁBufferedSocketǁrecv__mutmut_7, 
        'xǁBufferedSocketǁrecv__mutmut_8': xǁBufferedSocketǁrecv__mutmut_8, 
        'xǁBufferedSocketǁrecv__mutmut_9': xǁBufferedSocketǁrecv__mutmut_9, 
        'xǁBufferedSocketǁrecv__mutmut_10': xǁBufferedSocketǁrecv__mutmut_10, 
        'xǁBufferedSocketǁrecv__mutmut_11': xǁBufferedSocketǁrecv__mutmut_11, 
        'xǁBufferedSocketǁrecv__mutmut_12': xǁBufferedSocketǁrecv__mutmut_12, 
        'xǁBufferedSocketǁrecv__mutmut_13': xǁBufferedSocketǁrecv__mutmut_13, 
        'xǁBufferedSocketǁrecv__mutmut_14': xǁBufferedSocketǁrecv__mutmut_14, 
        'xǁBufferedSocketǁrecv__mutmut_15': xǁBufferedSocketǁrecv__mutmut_15, 
        'xǁBufferedSocketǁrecv__mutmut_16': xǁBufferedSocketǁrecv__mutmut_16, 
        'xǁBufferedSocketǁrecv__mutmut_17': xǁBufferedSocketǁrecv__mutmut_17, 
        'xǁBufferedSocketǁrecv__mutmut_18': xǁBufferedSocketǁrecv__mutmut_18, 
        'xǁBufferedSocketǁrecv__mutmut_19': xǁBufferedSocketǁrecv__mutmut_19
    }
    
    def recv(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁrecv__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁrecv__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recv.__signature__ = _mutmut_signature(xǁBufferedSocketǁrecv__mutmut_orig)
    xǁBufferedSocketǁrecv__mutmut_orig.__name__ = 'xǁBufferedSocketǁrecv'

    def xǁBufferedSocketǁpeek__mutmut_orig(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_1(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) > size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_2(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = None
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_3(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(None, timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_4(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=None)
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_5(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_6(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, )
            self.rbuf = data + self.rbuf
        return data

    def xǁBufferedSocketǁpeek__mutmut_7(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = None
        return data

    def xǁBufferedSocketǁpeek__mutmut_8(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are retained in BufferedSocket's internal recv buffer. To only
        see bytes in the recv buffer, use :meth:`getrecvbuffer`.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = data - self.rbuf
        return data
    
    xǁBufferedSocketǁpeek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁpeek__mutmut_1': xǁBufferedSocketǁpeek__mutmut_1, 
        'xǁBufferedSocketǁpeek__mutmut_2': xǁBufferedSocketǁpeek__mutmut_2, 
        'xǁBufferedSocketǁpeek__mutmut_3': xǁBufferedSocketǁpeek__mutmut_3, 
        'xǁBufferedSocketǁpeek__mutmut_4': xǁBufferedSocketǁpeek__mutmut_4, 
        'xǁBufferedSocketǁpeek__mutmut_5': xǁBufferedSocketǁpeek__mutmut_5, 
        'xǁBufferedSocketǁpeek__mutmut_6': xǁBufferedSocketǁpeek__mutmut_6, 
        'xǁBufferedSocketǁpeek__mutmut_7': xǁBufferedSocketǁpeek__mutmut_7, 
        'xǁBufferedSocketǁpeek__mutmut_8': xǁBufferedSocketǁpeek__mutmut_8
    }
    
    def peek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁpeek__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁpeek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    peek.__signature__ = _mutmut_signature(xǁBufferedSocketǁpeek__mutmut_orig)
    xǁBufferedSocketǁpeek__mutmut_orig.__name__ = 'xǁBufferedSocketǁpeek'

    def xǁBufferedSocketǁrecv_close__mutmut_orig(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_1(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is not _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_2(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = None
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_3(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is not None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_4(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = None
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_5(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = None
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_6(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(None, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_7(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, None)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_8(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_9(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, )
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_10(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize - 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_11(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 2, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_12(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = None
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_13(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b'XXXX'
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_14(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_15(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_16(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = None
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_17(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd - self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_18(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = None
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_19(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(None, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_20(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, None)
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_21(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_22(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, )
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def xǁBufferedSocketǁrecv_close__mutmut_23(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        # recv_close works by using recv_size to request maxsize data,
        # and ignoring ConnectionClose, returning and clearing the
        # internal buffer instead. It raises an exception if
        # ConnectionClosed isn't raised.
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(None)  # check receive buffer
        return ret
    
    xǁBufferedSocketǁrecv_close__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁrecv_close__mutmut_1': xǁBufferedSocketǁrecv_close__mutmut_1, 
        'xǁBufferedSocketǁrecv_close__mutmut_2': xǁBufferedSocketǁrecv_close__mutmut_2, 
        'xǁBufferedSocketǁrecv_close__mutmut_3': xǁBufferedSocketǁrecv_close__mutmut_3, 
        'xǁBufferedSocketǁrecv_close__mutmut_4': xǁBufferedSocketǁrecv_close__mutmut_4, 
        'xǁBufferedSocketǁrecv_close__mutmut_5': xǁBufferedSocketǁrecv_close__mutmut_5, 
        'xǁBufferedSocketǁrecv_close__mutmut_6': xǁBufferedSocketǁrecv_close__mutmut_6, 
        'xǁBufferedSocketǁrecv_close__mutmut_7': xǁBufferedSocketǁrecv_close__mutmut_7, 
        'xǁBufferedSocketǁrecv_close__mutmut_8': xǁBufferedSocketǁrecv_close__mutmut_8, 
        'xǁBufferedSocketǁrecv_close__mutmut_9': xǁBufferedSocketǁrecv_close__mutmut_9, 
        'xǁBufferedSocketǁrecv_close__mutmut_10': xǁBufferedSocketǁrecv_close__mutmut_10, 
        'xǁBufferedSocketǁrecv_close__mutmut_11': xǁBufferedSocketǁrecv_close__mutmut_11, 
        'xǁBufferedSocketǁrecv_close__mutmut_12': xǁBufferedSocketǁrecv_close__mutmut_12, 
        'xǁBufferedSocketǁrecv_close__mutmut_13': xǁBufferedSocketǁrecv_close__mutmut_13, 
        'xǁBufferedSocketǁrecv_close__mutmut_14': xǁBufferedSocketǁrecv_close__mutmut_14, 
        'xǁBufferedSocketǁrecv_close__mutmut_15': xǁBufferedSocketǁrecv_close__mutmut_15, 
        'xǁBufferedSocketǁrecv_close__mutmut_16': xǁBufferedSocketǁrecv_close__mutmut_16, 
        'xǁBufferedSocketǁrecv_close__mutmut_17': xǁBufferedSocketǁrecv_close__mutmut_17, 
        'xǁBufferedSocketǁrecv_close__mutmut_18': xǁBufferedSocketǁrecv_close__mutmut_18, 
        'xǁBufferedSocketǁrecv_close__mutmut_19': xǁBufferedSocketǁrecv_close__mutmut_19, 
        'xǁBufferedSocketǁrecv_close__mutmut_20': xǁBufferedSocketǁrecv_close__mutmut_20, 
        'xǁBufferedSocketǁrecv_close__mutmut_21': xǁBufferedSocketǁrecv_close__mutmut_21, 
        'xǁBufferedSocketǁrecv_close__mutmut_22': xǁBufferedSocketǁrecv_close__mutmut_22, 
        'xǁBufferedSocketǁrecv_close__mutmut_23': xǁBufferedSocketǁrecv_close__mutmut_23
    }
    
    def recv_close(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁrecv_close__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁrecv_close__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recv_close.__signature__ = _mutmut_signature(xǁBufferedSocketǁrecv_close__mutmut_orig)
    xǁBufferedSocketǁrecv_close__mutmut_orig.__name__ = 'xǁBufferedSocketǁrecv_close'

    def xǁBufferedSocketǁrecv_until__mutmut_orig(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_1(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=True):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_2(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is not _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_3(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = None
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_4(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is not None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_5(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = None
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_6(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is not _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_7(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = None
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_8(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = None

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_9(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = None
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_10(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = None
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_11(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(None)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_12(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = None
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_13(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = None  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_14(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 1  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_15(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_16(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(None)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_17(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 2:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_18(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = None
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_19(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(None, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_20(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, None, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_21(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, None)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_22(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_23(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_24(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, )
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_25(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.rfind(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_26(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset == -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_27(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != +1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_28(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -2:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_29(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset = len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_30(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset -= len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_31(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = None
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_32(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = None
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_33(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset - len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_34(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        return
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_35(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) >= maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_36(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(None, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_37(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, None)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_38(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_39(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, )  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_40(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = None
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_41(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout + (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_42(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() + start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_43(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout < 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_44(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 1.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_45(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(None)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_46(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = None
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_47(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(None)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_48(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_49(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = None
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_50(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = None
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_51(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' / args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_52(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('XXconnection closed after reading %s bytesXX'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_53(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('CONNECTION CLOSED AFTER READING %S BYTES'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_54(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               'XX without finding symbol: %rXX' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_55(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' WITHOUT FINDING SYMBOL: %R' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_56(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(None)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_57(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(None)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_58(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = None
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_59(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter - 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_60(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) + len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_61(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = +len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_62(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 2
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_63(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = None
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_64(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(None)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_65(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = None
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_66(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r' / (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_67(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('XXread %s bytes without finding delimiter: %rXX'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_68(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('READ %S BYTES WITHOUT FINDING DELIMITER: %R'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_69(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(None, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_70(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, None)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_71(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_72(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, )  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_73(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = None
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_74(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(None)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_75(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = None
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_76(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(None), bytes(recvd[rbuf_offset:])
        return val

    def xǁBufferedSocketǁrecv_until__mutmut_77(self, delimiter, timeout=_UNSET, maxsize=_UNSET,
                   with_delimiter=False):
        """Receive until *delimiter* is found, *maxsize* bytes have been read,
        or *timeout* is exceeded.

        Args:
            delimiter (bytes): One or more bytes to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
            with_delimiter (bool): Whether or not to include the
                delimiter in the output. ``False`` by default, but
                ``True`` is useful in cases where one is simply
                forwarding the messages.

        ``recv_until`` will raise the following exceptions:

          * :exc:`Timeout` if more than *timeout* seconds expire.
          * :exc:`ConnectionClosed` if the underlying socket is closed
            by the sending end.
          * :exc:`MessageTooLong` if the delimiter is not found in the
            first *maxsize* bytes.
          * :exc:`socket.error` if operating in nonblocking mode
            (*timeout* equal to 0), or if some unexpected socket error
            occurs, such as operating on a closed socket.

        """
        with self._recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout
            len_delimiter = len(delimiter)

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        if with_delimiter:  # include delimiter in return
                            offset += len_delimiter
                            rbuf_offset = offset
                        else:
                            rbuf_offset = offset + len_delimiter
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len_delimiter + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(None)
        return val
    
    xǁBufferedSocketǁrecv_until__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁrecv_until__mutmut_1': xǁBufferedSocketǁrecv_until__mutmut_1, 
        'xǁBufferedSocketǁrecv_until__mutmut_2': xǁBufferedSocketǁrecv_until__mutmut_2, 
        'xǁBufferedSocketǁrecv_until__mutmut_3': xǁBufferedSocketǁrecv_until__mutmut_3, 
        'xǁBufferedSocketǁrecv_until__mutmut_4': xǁBufferedSocketǁrecv_until__mutmut_4, 
        'xǁBufferedSocketǁrecv_until__mutmut_5': xǁBufferedSocketǁrecv_until__mutmut_5, 
        'xǁBufferedSocketǁrecv_until__mutmut_6': xǁBufferedSocketǁrecv_until__mutmut_6, 
        'xǁBufferedSocketǁrecv_until__mutmut_7': xǁBufferedSocketǁrecv_until__mutmut_7, 
        'xǁBufferedSocketǁrecv_until__mutmut_8': xǁBufferedSocketǁrecv_until__mutmut_8, 
        'xǁBufferedSocketǁrecv_until__mutmut_9': xǁBufferedSocketǁrecv_until__mutmut_9, 
        'xǁBufferedSocketǁrecv_until__mutmut_10': xǁBufferedSocketǁrecv_until__mutmut_10, 
        'xǁBufferedSocketǁrecv_until__mutmut_11': xǁBufferedSocketǁrecv_until__mutmut_11, 
        'xǁBufferedSocketǁrecv_until__mutmut_12': xǁBufferedSocketǁrecv_until__mutmut_12, 
        'xǁBufferedSocketǁrecv_until__mutmut_13': xǁBufferedSocketǁrecv_until__mutmut_13, 
        'xǁBufferedSocketǁrecv_until__mutmut_14': xǁBufferedSocketǁrecv_until__mutmut_14, 
        'xǁBufferedSocketǁrecv_until__mutmut_15': xǁBufferedSocketǁrecv_until__mutmut_15, 
        'xǁBufferedSocketǁrecv_until__mutmut_16': xǁBufferedSocketǁrecv_until__mutmut_16, 
        'xǁBufferedSocketǁrecv_until__mutmut_17': xǁBufferedSocketǁrecv_until__mutmut_17, 
        'xǁBufferedSocketǁrecv_until__mutmut_18': xǁBufferedSocketǁrecv_until__mutmut_18, 
        'xǁBufferedSocketǁrecv_until__mutmut_19': xǁBufferedSocketǁrecv_until__mutmut_19, 
        'xǁBufferedSocketǁrecv_until__mutmut_20': xǁBufferedSocketǁrecv_until__mutmut_20, 
        'xǁBufferedSocketǁrecv_until__mutmut_21': xǁBufferedSocketǁrecv_until__mutmut_21, 
        'xǁBufferedSocketǁrecv_until__mutmut_22': xǁBufferedSocketǁrecv_until__mutmut_22, 
        'xǁBufferedSocketǁrecv_until__mutmut_23': xǁBufferedSocketǁrecv_until__mutmut_23, 
        'xǁBufferedSocketǁrecv_until__mutmut_24': xǁBufferedSocketǁrecv_until__mutmut_24, 
        'xǁBufferedSocketǁrecv_until__mutmut_25': xǁBufferedSocketǁrecv_until__mutmut_25, 
        'xǁBufferedSocketǁrecv_until__mutmut_26': xǁBufferedSocketǁrecv_until__mutmut_26, 
        'xǁBufferedSocketǁrecv_until__mutmut_27': xǁBufferedSocketǁrecv_until__mutmut_27, 
        'xǁBufferedSocketǁrecv_until__mutmut_28': xǁBufferedSocketǁrecv_until__mutmut_28, 
        'xǁBufferedSocketǁrecv_until__mutmut_29': xǁBufferedSocketǁrecv_until__mutmut_29, 
        'xǁBufferedSocketǁrecv_until__mutmut_30': xǁBufferedSocketǁrecv_until__mutmut_30, 
        'xǁBufferedSocketǁrecv_until__mutmut_31': xǁBufferedSocketǁrecv_until__mutmut_31, 
        'xǁBufferedSocketǁrecv_until__mutmut_32': xǁBufferedSocketǁrecv_until__mutmut_32, 
        'xǁBufferedSocketǁrecv_until__mutmut_33': xǁBufferedSocketǁrecv_until__mutmut_33, 
        'xǁBufferedSocketǁrecv_until__mutmut_34': xǁBufferedSocketǁrecv_until__mutmut_34, 
        'xǁBufferedSocketǁrecv_until__mutmut_35': xǁBufferedSocketǁrecv_until__mutmut_35, 
        'xǁBufferedSocketǁrecv_until__mutmut_36': xǁBufferedSocketǁrecv_until__mutmut_36, 
        'xǁBufferedSocketǁrecv_until__mutmut_37': xǁBufferedSocketǁrecv_until__mutmut_37, 
        'xǁBufferedSocketǁrecv_until__mutmut_38': xǁBufferedSocketǁrecv_until__mutmut_38, 
        'xǁBufferedSocketǁrecv_until__mutmut_39': xǁBufferedSocketǁrecv_until__mutmut_39, 
        'xǁBufferedSocketǁrecv_until__mutmut_40': xǁBufferedSocketǁrecv_until__mutmut_40, 
        'xǁBufferedSocketǁrecv_until__mutmut_41': xǁBufferedSocketǁrecv_until__mutmut_41, 
        'xǁBufferedSocketǁrecv_until__mutmut_42': xǁBufferedSocketǁrecv_until__mutmut_42, 
        'xǁBufferedSocketǁrecv_until__mutmut_43': xǁBufferedSocketǁrecv_until__mutmut_43, 
        'xǁBufferedSocketǁrecv_until__mutmut_44': xǁBufferedSocketǁrecv_until__mutmut_44, 
        'xǁBufferedSocketǁrecv_until__mutmut_45': xǁBufferedSocketǁrecv_until__mutmut_45, 
        'xǁBufferedSocketǁrecv_until__mutmut_46': xǁBufferedSocketǁrecv_until__mutmut_46, 
        'xǁBufferedSocketǁrecv_until__mutmut_47': xǁBufferedSocketǁrecv_until__mutmut_47, 
        'xǁBufferedSocketǁrecv_until__mutmut_48': xǁBufferedSocketǁrecv_until__mutmut_48, 
        'xǁBufferedSocketǁrecv_until__mutmut_49': xǁBufferedSocketǁrecv_until__mutmut_49, 
        'xǁBufferedSocketǁrecv_until__mutmut_50': xǁBufferedSocketǁrecv_until__mutmut_50, 
        'xǁBufferedSocketǁrecv_until__mutmut_51': xǁBufferedSocketǁrecv_until__mutmut_51, 
        'xǁBufferedSocketǁrecv_until__mutmut_52': xǁBufferedSocketǁrecv_until__mutmut_52, 
        'xǁBufferedSocketǁrecv_until__mutmut_53': xǁBufferedSocketǁrecv_until__mutmut_53, 
        'xǁBufferedSocketǁrecv_until__mutmut_54': xǁBufferedSocketǁrecv_until__mutmut_54, 
        'xǁBufferedSocketǁrecv_until__mutmut_55': xǁBufferedSocketǁrecv_until__mutmut_55, 
        'xǁBufferedSocketǁrecv_until__mutmut_56': xǁBufferedSocketǁrecv_until__mutmut_56, 
        'xǁBufferedSocketǁrecv_until__mutmut_57': xǁBufferedSocketǁrecv_until__mutmut_57, 
        'xǁBufferedSocketǁrecv_until__mutmut_58': xǁBufferedSocketǁrecv_until__mutmut_58, 
        'xǁBufferedSocketǁrecv_until__mutmut_59': xǁBufferedSocketǁrecv_until__mutmut_59, 
        'xǁBufferedSocketǁrecv_until__mutmut_60': xǁBufferedSocketǁrecv_until__mutmut_60, 
        'xǁBufferedSocketǁrecv_until__mutmut_61': xǁBufferedSocketǁrecv_until__mutmut_61, 
        'xǁBufferedSocketǁrecv_until__mutmut_62': xǁBufferedSocketǁrecv_until__mutmut_62, 
        'xǁBufferedSocketǁrecv_until__mutmut_63': xǁBufferedSocketǁrecv_until__mutmut_63, 
        'xǁBufferedSocketǁrecv_until__mutmut_64': xǁBufferedSocketǁrecv_until__mutmut_64, 
        'xǁBufferedSocketǁrecv_until__mutmut_65': xǁBufferedSocketǁrecv_until__mutmut_65, 
        'xǁBufferedSocketǁrecv_until__mutmut_66': xǁBufferedSocketǁrecv_until__mutmut_66, 
        'xǁBufferedSocketǁrecv_until__mutmut_67': xǁBufferedSocketǁrecv_until__mutmut_67, 
        'xǁBufferedSocketǁrecv_until__mutmut_68': xǁBufferedSocketǁrecv_until__mutmut_68, 
        'xǁBufferedSocketǁrecv_until__mutmut_69': xǁBufferedSocketǁrecv_until__mutmut_69, 
        'xǁBufferedSocketǁrecv_until__mutmut_70': xǁBufferedSocketǁrecv_until__mutmut_70, 
        'xǁBufferedSocketǁrecv_until__mutmut_71': xǁBufferedSocketǁrecv_until__mutmut_71, 
        'xǁBufferedSocketǁrecv_until__mutmut_72': xǁBufferedSocketǁrecv_until__mutmut_72, 
        'xǁBufferedSocketǁrecv_until__mutmut_73': xǁBufferedSocketǁrecv_until__mutmut_73, 
        'xǁBufferedSocketǁrecv_until__mutmut_74': xǁBufferedSocketǁrecv_until__mutmut_74, 
        'xǁBufferedSocketǁrecv_until__mutmut_75': xǁBufferedSocketǁrecv_until__mutmut_75, 
        'xǁBufferedSocketǁrecv_until__mutmut_76': xǁBufferedSocketǁrecv_until__mutmut_76, 
        'xǁBufferedSocketǁrecv_until__mutmut_77': xǁBufferedSocketǁrecv_until__mutmut_77
    }
    
    def recv_until(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁrecv_until__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁrecv_until__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recv_until.__signature__ = _mutmut_signature(xǁBufferedSocketǁrecv_until__mutmut_orig)
    xǁBufferedSocketǁrecv_until__mutmut_orig.__name__ = 'xǁBufferedSocketǁrecv_until'

    def xǁBufferedSocketǁrecv_size__mutmut_orig(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_1(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is not _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_2(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = None
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_3(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = None
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_4(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = None
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_5(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 1
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_6(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = None
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_7(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(None)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_8(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = None
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_9(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf and self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_10(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(None)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_11(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes = len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_12(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes -= len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_13(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes > size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_14(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        return
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_15(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(None)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_16(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = None
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_17(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout + (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_18(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() + start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_19(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout < 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_20(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 1.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_21(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(None)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_22(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = None
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_23(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(None)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_24(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = None
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_25(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' / (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_26(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('XXconnection closed after reading %s of %s requestedXX'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_27(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('CONNECTION CLOSED AFTER READING %S OF %S REQUESTED'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_28(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           'XX bytesXX' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_29(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' BYTES' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_30(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(None)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_31(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = None
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_32(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(None)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_33(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b'XXXX'.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_34(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_35(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_36(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = None
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_37(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(None, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_38(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, None)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_39(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_40(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, )  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_41(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = None
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_42(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(None)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_43(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b'XXXX'.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_44(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_45(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_46(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = None
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_47(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes + size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_48(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = None
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_49(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:+extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_50(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[+extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_51(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = None
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_52(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b'XXXX'
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_53(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_54(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_55(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(None)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_56(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(None)

    def xǁBufferedSocketǁrecv_size__mutmut_57(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b'XXXX'.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_58(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def xǁBufferedSocketǁrecv_size__mutmut_59(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self._recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            chunks = []
            total_bytes = 0
            try:
                start = time.time()
                self.sock.settimeout(timeout)
                nxt = self.rbuf or self.sock.recv(self._recvsize)
                while nxt:
                    total_bytes += len(nxt)
                    if total_bytes >= size:
                        break
                    chunks.append(nxt)
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = f'read {total_bytes} of {size} bytes'
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)
    
    xǁBufferedSocketǁrecv_size__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁrecv_size__mutmut_1': xǁBufferedSocketǁrecv_size__mutmut_1, 
        'xǁBufferedSocketǁrecv_size__mutmut_2': xǁBufferedSocketǁrecv_size__mutmut_2, 
        'xǁBufferedSocketǁrecv_size__mutmut_3': xǁBufferedSocketǁrecv_size__mutmut_3, 
        'xǁBufferedSocketǁrecv_size__mutmut_4': xǁBufferedSocketǁrecv_size__mutmut_4, 
        'xǁBufferedSocketǁrecv_size__mutmut_5': xǁBufferedSocketǁrecv_size__mutmut_5, 
        'xǁBufferedSocketǁrecv_size__mutmut_6': xǁBufferedSocketǁrecv_size__mutmut_6, 
        'xǁBufferedSocketǁrecv_size__mutmut_7': xǁBufferedSocketǁrecv_size__mutmut_7, 
        'xǁBufferedSocketǁrecv_size__mutmut_8': xǁBufferedSocketǁrecv_size__mutmut_8, 
        'xǁBufferedSocketǁrecv_size__mutmut_9': xǁBufferedSocketǁrecv_size__mutmut_9, 
        'xǁBufferedSocketǁrecv_size__mutmut_10': xǁBufferedSocketǁrecv_size__mutmut_10, 
        'xǁBufferedSocketǁrecv_size__mutmut_11': xǁBufferedSocketǁrecv_size__mutmut_11, 
        'xǁBufferedSocketǁrecv_size__mutmut_12': xǁBufferedSocketǁrecv_size__mutmut_12, 
        'xǁBufferedSocketǁrecv_size__mutmut_13': xǁBufferedSocketǁrecv_size__mutmut_13, 
        'xǁBufferedSocketǁrecv_size__mutmut_14': xǁBufferedSocketǁrecv_size__mutmut_14, 
        'xǁBufferedSocketǁrecv_size__mutmut_15': xǁBufferedSocketǁrecv_size__mutmut_15, 
        'xǁBufferedSocketǁrecv_size__mutmut_16': xǁBufferedSocketǁrecv_size__mutmut_16, 
        'xǁBufferedSocketǁrecv_size__mutmut_17': xǁBufferedSocketǁrecv_size__mutmut_17, 
        'xǁBufferedSocketǁrecv_size__mutmut_18': xǁBufferedSocketǁrecv_size__mutmut_18, 
        'xǁBufferedSocketǁrecv_size__mutmut_19': xǁBufferedSocketǁrecv_size__mutmut_19, 
        'xǁBufferedSocketǁrecv_size__mutmut_20': xǁBufferedSocketǁrecv_size__mutmut_20, 
        'xǁBufferedSocketǁrecv_size__mutmut_21': xǁBufferedSocketǁrecv_size__mutmut_21, 
        'xǁBufferedSocketǁrecv_size__mutmut_22': xǁBufferedSocketǁrecv_size__mutmut_22, 
        'xǁBufferedSocketǁrecv_size__mutmut_23': xǁBufferedSocketǁrecv_size__mutmut_23, 
        'xǁBufferedSocketǁrecv_size__mutmut_24': xǁBufferedSocketǁrecv_size__mutmut_24, 
        'xǁBufferedSocketǁrecv_size__mutmut_25': xǁBufferedSocketǁrecv_size__mutmut_25, 
        'xǁBufferedSocketǁrecv_size__mutmut_26': xǁBufferedSocketǁrecv_size__mutmut_26, 
        'xǁBufferedSocketǁrecv_size__mutmut_27': xǁBufferedSocketǁrecv_size__mutmut_27, 
        'xǁBufferedSocketǁrecv_size__mutmut_28': xǁBufferedSocketǁrecv_size__mutmut_28, 
        'xǁBufferedSocketǁrecv_size__mutmut_29': xǁBufferedSocketǁrecv_size__mutmut_29, 
        'xǁBufferedSocketǁrecv_size__mutmut_30': xǁBufferedSocketǁrecv_size__mutmut_30, 
        'xǁBufferedSocketǁrecv_size__mutmut_31': xǁBufferedSocketǁrecv_size__mutmut_31, 
        'xǁBufferedSocketǁrecv_size__mutmut_32': xǁBufferedSocketǁrecv_size__mutmut_32, 
        'xǁBufferedSocketǁrecv_size__mutmut_33': xǁBufferedSocketǁrecv_size__mutmut_33, 
        'xǁBufferedSocketǁrecv_size__mutmut_34': xǁBufferedSocketǁrecv_size__mutmut_34, 
        'xǁBufferedSocketǁrecv_size__mutmut_35': xǁBufferedSocketǁrecv_size__mutmut_35, 
        'xǁBufferedSocketǁrecv_size__mutmut_36': xǁBufferedSocketǁrecv_size__mutmut_36, 
        'xǁBufferedSocketǁrecv_size__mutmut_37': xǁBufferedSocketǁrecv_size__mutmut_37, 
        'xǁBufferedSocketǁrecv_size__mutmut_38': xǁBufferedSocketǁrecv_size__mutmut_38, 
        'xǁBufferedSocketǁrecv_size__mutmut_39': xǁBufferedSocketǁrecv_size__mutmut_39, 
        'xǁBufferedSocketǁrecv_size__mutmut_40': xǁBufferedSocketǁrecv_size__mutmut_40, 
        'xǁBufferedSocketǁrecv_size__mutmut_41': xǁBufferedSocketǁrecv_size__mutmut_41, 
        'xǁBufferedSocketǁrecv_size__mutmut_42': xǁBufferedSocketǁrecv_size__mutmut_42, 
        'xǁBufferedSocketǁrecv_size__mutmut_43': xǁBufferedSocketǁrecv_size__mutmut_43, 
        'xǁBufferedSocketǁrecv_size__mutmut_44': xǁBufferedSocketǁrecv_size__mutmut_44, 
        'xǁBufferedSocketǁrecv_size__mutmut_45': xǁBufferedSocketǁrecv_size__mutmut_45, 
        'xǁBufferedSocketǁrecv_size__mutmut_46': xǁBufferedSocketǁrecv_size__mutmut_46, 
        'xǁBufferedSocketǁrecv_size__mutmut_47': xǁBufferedSocketǁrecv_size__mutmut_47, 
        'xǁBufferedSocketǁrecv_size__mutmut_48': xǁBufferedSocketǁrecv_size__mutmut_48, 
        'xǁBufferedSocketǁrecv_size__mutmut_49': xǁBufferedSocketǁrecv_size__mutmut_49, 
        'xǁBufferedSocketǁrecv_size__mutmut_50': xǁBufferedSocketǁrecv_size__mutmut_50, 
        'xǁBufferedSocketǁrecv_size__mutmut_51': xǁBufferedSocketǁrecv_size__mutmut_51, 
        'xǁBufferedSocketǁrecv_size__mutmut_52': xǁBufferedSocketǁrecv_size__mutmut_52, 
        'xǁBufferedSocketǁrecv_size__mutmut_53': xǁBufferedSocketǁrecv_size__mutmut_53, 
        'xǁBufferedSocketǁrecv_size__mutmut_54': xǁBufferedSocketǁrecv_size__mutmut_54, 
        'xǁBufferedSocketǁrecv_size__mutmut_55': xǁBufferedSocketǁrecv_size__mutmut_55, 
        'xǁBufferedSocketǁrecv_size__mutmut_56': xǁBufferedSocketǁrecv_size__mutmut_56, 
        'xǁBufferedSocketǁrecv_size__mutmut_57': xǁBufferedSocketǁrecv_size__mutmut_57, 
        'xǁBufferedSocketǁrecv_size__mutmut_58': xǁBufferedSocketǁrecv_size__mutmut_58, 
        'xǁBufferedSocketǁrecv_size__mutmut_59': xǁBufferedSocketǁrecv_size__mutmut_59
    }
    
    def recv_size(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁrecv_size__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁrecv_size__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recv_size.__signature__ = _mutmut_signature(xǁBufferedSocketǁrecv_size__mutmut_orig)
    xǁBufferedSocketǁrecv_size__mutmut_orig.__name__ = 'xǁBufferedSocketǁrecv_size'

    def xǁBufferedSocketǁsend__mutmut_orig(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_1(self, data, flags=1, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_2(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is not _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_3(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = None
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_4(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError(None)
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_5(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("XXnon-zero flags not supportedXX")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_6(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("NON-ZERO FLAGS NOT SUPPORTED")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_7(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = None
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_8(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(None)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_9(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) >= 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_10(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 2:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_11(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = None
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_12(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join(None)]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_13(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b'XXXX'.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_14(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_15(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_16(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(None)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_17(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = None
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_18(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 1
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_19(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[1]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_20(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = None
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_21(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(None)
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_22(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[1])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_23(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent = sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_24(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent -= sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_25(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = None
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_26(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[1] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_27(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[1][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_28(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = None
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_29(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout + (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_30(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() + start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_31(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout < 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_32(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 1.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_33(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(None)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_34(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(None, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_35(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, None)
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_36(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout('%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_37(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, )
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_38(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' / len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_39(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, 'XX%s bytes unsentXX' % len(sbuf[0]))
        return total_sent

    def xǁBufferedSocketǁsend__mutmut_40(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.
        """
        with self._send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%S BYTES UNSENT' % len(sbuf[0]))
        return total_sent
    
    xǁBufferedSocketǁsend__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsend__mutmut_1': xǁBufferedSocketǁsend__mutmut_1, 
        'xǁBufferedSocketǁsend__mutmut_2': xǁBufferedSocketǁsend__mutmut_2, 
        'xǁBufferedSocketǁsend__mutmut_3': xǁBufferedSocketǁsend__mutmut_3, 
        'xǁBufferedSocketǁsend__mutmut_4': xǁBufferedSocketǁsend__mutmut_4, 
        'xǁBufferedSocketǁsend__mutmut_5': xǁBufferedSocketǁsend__mutmut_5, 
        'xǁBufferedSocketǁsend__mutmut_6': xǁBufferedSocketǁsend__mutmut_6, 
        'xǁBufferedSocketǁsend__mutmut_7': xǁBufferedSocketǁsend__mutmut_7, 
        'xǁBufferedSocketǁsend__mutmut_8': xǁBufferedSocketǁsend__mutmut_8, 
        'xǁBufferedSocketǁsend__mutmut_9': xǁBufferedSocketǁsend__mutmut_9, 
        'xǁBufferedSocketǁsend__mutmut_10': xǁBufferedSocketǁsend__mutmut_10, 
        'xǁBufferedSocketǁsend__mutmut_11': xǁBufferedSocketǁsend__mutmut_11, 
        'xǁBufferedSocketǁsend__mutmut_12': xǁBufferedSocketǁsend__mutmut_12, 
        'xǁBufferedSocketǁsend__mutmut_13': xǁBufferedSocketǁsend__mutmut_13, 
        'xǁBufferedSocketǁsend__mutmut_14': xǁBufferedSocketǁsend__mutmut_14, 
        'xǁBufferedSocketǁsend__mutmut_15': xǁBufferedSocketǁsend__mutmut_15, 
        'xǁBufferedSocketǁsend__mutmut_16': xǁBufferedSocketǁsend__mutmut_16, 
        'xǁBufferedSocketǁsend__mutmut_17': xǁBufferedSocketǁsend__mutmut_17, 
        'xǁBufferedSocketǁsend__mutmut_18': xǁBufferedSocketǁsend__mutmut_18, 
        'xǁBufferedSocketǁsend__mutmut_19': xǁBufferedSocketǁsend__mutmut_19, 
        'xǁBufferedSocketǁsend__mutmut_20': xǁBufferedSocketǁsend__mutmut_20, 
        'xǁBufferedSocketǁsend__mutmut_21': xǁBufferedSocketǁsend__mutmut_21, 
        'xǁBufferedSocketǁsend__mutmut_22': xǁBufferedSocketǁsend__mutmut_22, 
        'xǁBufferedSocketǁsend__mutmut_23': xǁBufferedSocketǁsend__mutmut_23, 
        'xǁBufferedSocketǁsend__mutmut_24': xǁBufferedSocketǁsend__mutmut_24, 
        'xǁBufferedSocketǁsend__mutmut_25': xǁBufferedSocketǁsend__mutmut_25, 
        'xǁBufferedSocketǁsend__mutmut_26': xǁBufferedSocketǁsend__mutmut_26, 
        'xǁBufferedSocketǁsend__mutmut_27': xǁBufferedSocketǁsend__mutmut_27, 
        'xǁBufferedSocketǁsend__mutmut_28': xǁBufferedSocketǁsend__mutmut_28, 
        'xǁBufferedSocketǁsend__mutmut_29': xǁBufferedSocketǁsend__mutmut_29, 
        'xǁBufferedSocketǁsend__mutmut_30': xǁBufferedSocketǁsend__mutmut_30, 
        'xǁBufferedSocketǁsend__mutmut_31': xǁBufferedSocketǁsend__mutmut_31, 
        'xǁBufferedSocketǁsend__mutmut_32': xǁBufferedSocketǁsend__mutmut_32, 
        'xǁBufferedSocketǁsend__mutmut_33': xǁBufferedSocketǁsend__mutmut_33, 
        'xǁBufferedSocketǁsend__mutmut_34': xǁBufferedSocketǁsend__mutmut_34, 
        'xǁBufferedSocketǁsend__mutmut_35': xǁBufferedSocketǁsend__mutmut_35, 
        'xǁBufferedSocketǁsend__mutmut_36': xǁBufferedSocketǁsend__mutmut_36, 
        'xǁBufferedSocketǁsend__mutmut_37': xǁBufferedSocketǁsend__mutmut_37, 
        'xǁBufferedSocketǁsend__mutmut_38': xǁBufferedSocketǁsend__mutmut_38, 
        'xǁBufferedSocketǁsend__mutmut_39': xǁBufferedSocketǁsend__mutmut_39, 
        'xǁBufferedSocketǁsend__mutmut_40': xǁBufferedSocketǁsend__mutmut_40
    }
    
    def send(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsend__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsend__mutmut_mutants"), args, kwargs, self)
        return result 
    
    send.__signature__ = _mutmut_signature(xǁBufferedSocketǁsend__mutmut_orig)
    xǁBufferedSocketǁsend__mutmut_orig.__name__ = 'xǁBufferedSocketǁsend'

    def xǁBufferedSocketǁsendall__mutmut_orig(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, timeout)

    def xǁBufferedSocketǁsendall__mutmut_1(self, data, flags=1, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, timeout)

    def xǁBufferedSocketǁsendall__mutmut_2(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(None, flags, timeout)

    def xǁBufferedSocketǁsendall__mutmut_3(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, None, timeout)

    def xǁBufferedSocketǁsendall__mutmut_4(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, None)

    def xǁBufferedSocketǁsendall__mutmut_5(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(flags, timeout)

    def xǁBufferedSocketǁsendall__mutmut_6(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, timeout)

    def xǁBufferedSocketǁsendall__mutmut_7(self, data, flags=0, timeout=_UNSET):
        """A passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, )
    
    xǁBufferedSocketǁsendall__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsendall__mutmut_1': xǁBufferedSocketǁsendall__mutmut_1, 
        'xǁBufferedSocketǁsendall__mutmut_2': xǁBufferedSocketǁsendall__mutmut_2, 
        'xǁBufferedSocketǁsendall__mutmut_3': xǁBufferedSocketǁsendall__mutmut_3, 
        'xǁBufferedSocketǁsendall__mutmut_4': xǁBufferedSocketǁsendall__mutmut_4, 
        'xǁBufferedSocketǁsendall__mutmut_5': xǁBufferedSocketǁsendall__mutmut_5, 
        'xǁBufferedSocketǁsendall__mutmut_6': xǁBufferedSocketǁsendall__mutmut_6, 
        'xǁBufferedSocketǁsendall__mutmut_7': xǁBufferedSocketǁsendall__mutmut_7
    }
    
    def sendall(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsendall__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsendall__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sendall.__signature__ = _mutmut_signature(xǁBufferedSocketǁsendall__mutmut_orig)
    xǁBufferedSocketǁsendall__mutmut_orig.__name__ = 'xǁBufferedSocketǁsendall'

    def xǁBufferedSocketǁflush__mutmut_orig(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'')
        return

    def xǁBufferedSocketǁflush__mutmut_1(self):
        "XXSend the contents of the internal send buffer.XX"
        with self._send_lock:
            self.send(b'')
        return

    def xǁBufferedSocketǁflush__mutmut_2(self):
        "send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'')
        return

    def xǁBufferedSocketǁflush__mutmut_3(self):
        "SEND THE CONTENTS OF THE INTERNAL SEND BUFFER."
        with self._send_lock:
            self.send(b'')
        return

    def xǁBufferedSocketǁflush__mutmut_4(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(None)
        return

    def xǁBufferedSocketǁflush__mutmut_5(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'XXXX')
        return

    def xǁBufferedSocketǁflush__mutmut_6(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'')
        return

    def xǁBufferedSocketǁflush__mutmut_7(self):
        "Send the contents of the internal send buffer."
        with self._send_lock:
            self.send(b'')
        return
    
    xǁBufferedSocketǁflush__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁflush__mutmut_1': xǁBufferedSocketǁflush__mutmut_1, 
        'xǁBufferedSocketǁflush__mutmut_2': xǁBufferedSocketǁflush__mutmut_2, 
        'xǁBufferedSocketǁflush__mutmut_3': xǁBufferedSocketǁflush__mutmut_3, 
        'xǁBufferedSocketǁflush__mutmut_4': xǁBufferedSocketǁflush__mutmut_4, 
        'xǁBufferedSocketǁflush__mutmut_5': xǁBufferedSocketǁflush__mutmut_5, 
        'xǁBufferedSocketǁflush__mutmut_6': xǁBufferedSocketǁflush__mutmut_6, 
        'xǁBufferedSocketǁflush__mutmut_7': xǁBufferedSocketǁflush__mutmut_7
    }
    
    def flush(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁflush__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁflush__mutmut_mutants"), args, kwargs, self)
        return result 
    
    flush.__signature__ = _mutmut_signature(xǁBufferedSocketǁflush__mutmut_orig)
    xǁBufferedSocketǁflush__mutmut_orig.__name__ = 'xǁBufferedSocketǁflush'

    def xǁBufferedSocketǁbuffer__mutmut_orig(self, data):
        "Buffer *data* bytes for the next send operation."
        with self._send_lock:
            self.sbuf.append(data)
        return

    def xǁBufferedSocketǁbuffer__mutmut_1(self, data):
        "XXBuffer *data* bytes for the next send operation.XX"
        with self._send_lock:
            self.sbuf.append(data)
        return

    def xǁBufferedSocketǁbuffer__mutmut_2(self, data):
        "buffer *data* bytes for the next send operation."
        with self._send_lock:
            self.sbuf.append(data)
        return

    def xǁBufferedSocketǁbuffer__mutmut_3(self, data):
        "BUFFER *DATA* BYTES FOR THE NEXT SEND OPERATION."
        with self._send_lock:
            self.sbuf.append(data)
        return

    def xǁBufferedSocketǁbuffer__mutmut_4(self, data):
        "Buffer *data* bytes for the next send operation."
        with self._send_lock:
            self.sbuf.append(None)
        return
    
    xǁBufferedSocketǁbuffer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁbuffer__mutmut_1': xǁBufferedSocketǁbuffer__mutmut_1, 
        'xǁBufferedSocketǁbuffer__mutmut_2': xǁBufferedSocketǁbuffer__mutmut_2, 
        'xǁBufferedSocketǁbuffer__mutmut_3': xǁBufferedSocketǁbuffer__mutmut_3, 
        'xǁBufferedSocketǁbuffer__mutmut_4': xǁBufferedSocketǁbuffer__mutmut_4
    }
    
    def buffer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁbuffer__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁbuffer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    buffer.__signature__ = _mutmut_signature(xǁBufferedSocketǁbuffer__mutmut_orig)
    xǁBufferedSocketǁbuffer__mutmut_orig.__name__ = 'xǁBufferedSocketǁbuffer'

    # # #
    # # # Passing through some socket basics
    # # #

    def getsockname(self):
        """Convenience function to return the wrapped socket's own address.
        See :meth:`socket.getsockname` for more details.
        """
        return self.sock.getsockname()

    def getpeername(self):
        """Convenience function to return the remote address to which the
        wrapped socket is connected.  See :meth:`socket.getpeername`
        for more details.
        """
        return self.sock.getpeername()

    def xǁBufferedSocketǁgetsockopt__mutmut_orig(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = (level, optname)
        if buflen is not None:
            args += (buflen,)
        return self.sock.getsockopt(*args)

    def xǁBufferedSocketǁgetsockopt__mutmut_1(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = None
        if buflen is not None:
            args += (buflen,)
        return self.sock.getsockopt(*args)

    def xǁBufferedSocketǁgetsockopt__mutmut_2(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = (level, optname)
        if buflen is None:
            args += (buflen,)
        return self.sock.getsockopt(*args)

    def xǁBufferedSocketǁgetsockopt__mutmut_3(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = (level, optname)
        if buflen is not None:
            args = (buflen,)
        return self.sock.getsockopt(*args)

    def xǁBufferedSocketǁgetsockopt__mutmut_4(self, level, optname, buflen=None):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.getsockopt`.
        """
        args = (level, optname)
        if buflen is not None:
            args -= (buflen,)
        return self.sock.getsockopt(*args)
    
    xǁBufferedSocketǁgetsockopt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁgetsockopt__mutmut_1': xǁBufferedSocketǁgetsockopt__mutmut_1, 
        'xǁBufferedSocketǁgetsockopt__mutmut_2': xǁBufferedSocketǁgetsockopt__mutmut_2, 
        'xǁBufferedSocketǁgetsockopt__mutmut_3': xǁBufferedSocketǁgetsockopt__mutmut_3, 
        'xǁBufferedSocketǁgetsockopt__mutmut_4': xǁBufferedSocketǁgetsockopt__mutmut_4
    }
    
    def getsockopt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁgetsockopt__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁgetsockopt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    getsockopt.__signature__ = _mutmut_signature(xǁBufferedSocketǁgetsockopt__mutmut_orig)
    xǁBufferedSocketǁgetsockopt__mutmut_orig.__name__ = 'xǁBufferedSocketǁgetsockopt'

    def xǁBufferedSocketǁsetsockopt__mutmut_orig(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, optname, value)

    def xǁBufferedSocketǁsetsockopt__mutmut_1(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(None, optname, value)

    def xǁBufferedSocketǁsetsockopt__mutmut_2(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, None, value)

    def xǁBufferedSocketǁsetsockopt__mutmut_3(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, optname, None)

    def xǁBufferedSocketǁsetsockopt__mutmut_4(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(optname, value)

    def xǁBufferedSocketǁsetsockopt__mutmut_5(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, value)

    def xǁBufferedSocketǁsetsockopt__mutmut_6(self, level, optname, value):
        """Convenience function passing through to the wrapped socket's
        :meth:`socket.setsockopt`.
        """
        return self.sock.setsockopt(level, optname, )
    
    xǁBufferedSocketǁsetsockopt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁsetsockopt__mutmut_1': xǁBufferedSocketǁsetsockopt__mutmut_1, 
        'xǁBufferedSocketǁsetsockopt__mutmut_2': xǁBufferedSocketǁsetsockopt__mutmut_2, 
        'xǁBufferedSocketǁsetsockopt__mutmut_3': xǁBufferedSocketǁsetsockopt__mutmut_3, 
        'xǁBufferedSocketǁsetsockopt__mutmut_4': xǁBufferedSocketǁsetsockopt__mutmut_4, 
        'xǁBufferedSocketǁsetsockopt__mutmut_5': xǁBufferedSocketǁsetsockopt__mutmut_5, 
        'xǁBufferedSocketǁsetsockopt__mutmut_6': xǁBufferedSocketǁsetsockopt__mutmut_6
    }
    
    def setsockopt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁsetsockopt__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁsetsockopt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setsockopt.__signature__ = _mutmut_signature(xǁBufferedSocketǁsetsockopt__mutmut_orig)
    xǁBufferedSocketǁsetsockopt__mutmut_orig.__name__ = 'xǁBufferedSocketǁsetsockopt'

    @property
    def type(self):
        """A passthrough to the wrapped socket's type. Valid usages should
        only ever see :data:`socket.SOCK_STREAM`.
        """
        return self.sock.type

    @property
    def family(self):
        """A passthrough to the wrapped socket's family. BufferedSocket
        supports all widely-used families, so this read-only attribute
        can be one of :data:`socket.AF_INET` for IP,
        :data:`socket.AF_INET6` for IPv6, and :data:`socket.AF_UNIX`
        for UDS.
        """
        return self.sock.family

    @property
    def proto(self):
        """A passthrough to the wrapped socket's protocol. The ``proto``
        attribute is very rarely used, so it's always 0, meaning "the
        default" protocol. Pretty much all the practical information
        is in :attr:`~BufferedSocket.type` and
        :attr:`~BufferedSocket.family`, so you can go back to never
        thinking about this.
        """
        return self.sock.proto

    # # #
    # # # Now for some more advanced interpretations of the builtin socket
    # # #

    def fileno(self):
        """Returns the file descriptor of the wrapped socket. -1 if it has
        been closed on this end.

        Note that this makes the BufferedSocket selectable, i.e.,
        usable for operating system event loops without any external
        libraries. Keep in mind that the operating system cannot know
        about data in BufferedSocket's internal buffer. Exercise
        discipline with calling ``recv*`` functions.
        """
        return self.sock.fileno()

    def xǁBufferedSocketǁclose__mutmut_orig(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_1(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = None
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_2(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b'XXXX'
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_3(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_4(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_5(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = None
                self.sbuf[:] = []
                self.sock.close()
        return

    def xǁBufferedSocketǁclose__mutmut_6(self):
        """Closes the wrapped socket, and empties the internal buffers. The
        send buffer is not flushed automatically, so if you have been
        calling :meth:`~BufferedSocket.buffer`, be sure to call
        :meth:`~BufferedSocket.flush` before calling this
        method. After calling this method, future socket operations
        will raise :exc:`socket.error`.
        """
        with self._recv_lock:
            with self._send_lock:
                self.rbuf = b''
                self.rbuf_unconsumed = self.rbuf
                self.sbuf[:] = None
                self.sock.close()
        return
    
    xǁBufferedSocketǁclose__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁclose__mutmut_1': xǁBufferedSocketǁclose__mutmut_1, 
        'xǁBufferedSocketǁclose__mutmut_2': xǁBufferedSocketǁclose__mutmut_2, 
        'xǁBufferedSocketǁclose__mutmut_3': xǁBufferedSocketǁclose__mutmut_3, 
        'xǁBufferedSocketǁclose__mutmut_4': xǁBufferedSocketǁclose__mutmut_4, 
        'xǁBufferedSocketǁclose__mutmut_5': xǁBufferedSocketǁclose__mutmut_5, 
        'xǁBufferedSocketǁclose__mutmut_6': xǁBufferedSocketǁclose__mutmut_6
    }
    
    def close(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁclose__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁclose__mutmut_mutants"), args, kwargs, self)
        return result 
    
    close.__signature__ = _mutmut_signature(xǁBufferedSocketǁclose__mutmut_orig)
    xǁBufferedSocketǁclose__mutmut_orig.__name__ = 'xǁBufferedSocketǁclose'

    def xǁBufferedSocketǁshutdown__mutmut_orig(self, how):
        """Convenience method which passes through to the wrapped socket's
        :meth:`~socket.shutdown`. Semantics vary by platform, so no
        special internal handling is done with the buffers. This
        method exists to facilitate the most common usage, wherein a
        full ``shutdown`` is followed by a
        :meth:`~BufferedSocket.close`. Developers requiring more
        support, please open `an issue`_.

        .. _an issue: https://github.com/mahmoud/boltons/issues
        """
        with self._recv_lock:
            with self._send_lock:
                self.sock.shutdown(how)
        return

    def xǁBufferedSocketǁshutdown__mutmut_1(self, how):
        """Convenience method which passes through to the wrapped socket's
        :meth:`~socket.shutdown`. Semantics vary by platform, so no
        special internal handling is done with the buffers. This
        method exists to facilitate the most common usage, wherein a
        full ``shutdown`` is followed by a
        :meth:`~BufferedSocket.close`. Developers requiring more
        support, please open `an issue`_.

        .. _an issue: https://github.com/mahmoud/boltons/issues
        """
        with self._recv_lock:
            with self._send_lock:
                self.sock.shutdown(None)
        return
    
    xǁBufferedSocketǁshutdown__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBufferedSocketǁshutdown__mutmut_1': xǁBufferedSocketǁshutdown__mutmut_1
    }
    
    def shutdown(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBufferedSocketǁshutdown__mutmut_orig"), object.__getattribute__(self, "xǁBufferedSocketǁshutdown__mutmut_mutants"), args, kwargs, self)
        return result 
    
    shutdown.__signature__ = _mutmut_signature(xǁBufferedSocketǁshutdown__mutmut_orig)
    xǁBufferedSocketǁshutdown__mutmut_orig.__name__ = 'xǁBufferedSocketǁshutdown'

    # end BufferedSocket


class Error(socket.error):
    """A subclass of :exc:`socket.error` from which all other
    ``socketutils`` exceptions inherit.

    When using :class:`BufferedSocket` and other ``socketutils``
    types, generally you want to catch one of the specific exception
    types below, or :exc:`socket.error`.
    """
    pass


class ConnectionClosed(Error):
    """Raised when receiving and the connection is unexpectedly closed
    from the sending end. Raised from :class:`BufferedSocket`'s
    :meth:`~BufferedSocket.peek`, :meth:`~BufferedSocket.recv_until`,
    and :meth:`~BufferedSocket.recv_size`, and never from its
    :meth:`~BufferedSocket.recv` or
    :meth:`~BufferedSocket.recv_close`.
    """
    pass


class MessageTooLong(Error):
    """Raised from :meth:`BufferedSocket.recv_until` and
    :meth:`BufferedSocket.recv_closed` when more than *maxsize* bytes are
    read without encountering the delimiter or a closed connection,
    respectively.
    """
    def xǁMessageTooLongǁ__init____mutmut_orig(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_1(self, bytes_read=None, delimiter=None):
        msg = None
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_2(self, bytes_read=None, delimiter=None):
        msg = 'XXmessage exceeded maximum sizeXX'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_3(self, bytes_read=None, delimiter=None):
        msg = 'MESSAGE EXCEEDED MAXIMUM SIZE'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_4(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_5(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg = f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_6(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg -= f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_7(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_8(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg = f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_9(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg -= f'. Delimiter not found: {delimiter!r}'
        super().__init__(msg)
    def xǁMessageTooLongǁ__init____mutmut_10(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += f'. {bytes_read} bytes read'
        if delimiter is not None:
            msg += f'. Delimiter not found: {delimiter!r}'
        super().__init__(None)
    
    xǁMessageTooLongǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMessageTooLongǁ__init____mutmut_1': xǁMessageTooLongǁ__init____mutmut_1, 
        'xǁMessageTooLongǁ__init____mutmut_2': xǁMessageTooLongǁ__init____mutmut_2, 
        'xǁMessageTooLongǁ__init____mutmut_3': xǁMessageTooLongǁ__init____mutmut_3, 
        'xǁMessageTooLongǁ__init____mutmut_4': xǁMessageTooLongǁ__init____mutmut_4, 
        'xǁMessageTooLongǁ__init____mutmut_5': xǁMessageTooLongǁ__init____mutmut_5, 
        'xǁMessageTooLongǁ__init____mutmut_6': xǁMessageTooLongǁ__init____mutmut_6, 
        'xǁMessageTooLongǁ__init____mutmut_7': xǁMessageTooLongǁ__init____mutmut_7, 
        'xǁMessageTooLongǁ__init____mutmut_8': xǁMessageTooLongǁ__init____mutmut_8, 
        'xǁMessageTooLongǁ__init____mutmut_9': xǁMessageTooLongǁ__init____mutmut_9, 
        'xǁMessageTooLongǁ__init____mutmut_10': xǁMessageTooLongǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMessageTooLongǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMessageTooLongǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMessageTooLongǁ__init____mutmut_orig)
    xǁMessageTooLongǁ__init____mutmut_orig.__name__ = 'xǁMessageTooLongǁ__init__'


class Timeout(socket.timeout, Error):
    """Inheriting from :exc:`socket.timeout`, Timeout is used to indicate
    when a socket operation did not complete within the time
    specified. Raised from any of :class:`BufferedSocket`'s ``recv``
    methods.
    """
    def xǁTimeoutǁ__init____mutmut_orig(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_1(self, timeout, extra="XXXX"):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_2(self, timeout, extra=""):
        msg = None
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_3(self, timeout, extra=""):
        msg = 'XXsocket operation timed outXX'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_4(self, timeout, extra=""):
        msg = 'SOCKET OPERATION TIMED OUT'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_5(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_6(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg = ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_7(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg -= ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_8(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' / (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_9(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += 'XX after %sms.XX' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_10(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' AFTER %SMS.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_11(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout / 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_12(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1001)
        if extra:
            msg += ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_13(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg = ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_14(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg -= ' ' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_15(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' - extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_16(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += 'XX XX' + extra
        super().__init__(msg)
    def xǁTimeoutǁ__init____mutmut_17(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms.' % (timeout * 1000)
        if extra:
            msg += ' ' + extra
        super().__init__(None)
    
    xǁTimeoutǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTimeoutǁ__init____mutmut_1': xǁTimeoutǁ__init____mutmut_1, 
        'xǁTimeoutǁ__init____mutmut_2': xǁTimeoutǁ__init____mutmut_2, 
        'xǁTimeoutǁ__init____mutmut_3': xǁTimeoutǁ__init____mutmut_3, 
        'xǁTimeoutǁ__init____mutmut_4': xǁTimeoutǁ__init____mutmut_4, 
        'xǁTimeoutǁ__init____mutmut_5': xǁTimeoutǁ__init____mutmut_5, 
        'xǁTimeoutǁ__init____mutmut_6': xǁTimeoutǁ__init____mutmut_6, 
        'xǁTimeoutǁ__init____mutmut_7': xǁTimeoutǁ__init____mutmut_7, 
        'xǁTimeoutǁ__init____mutmut_8': xǁTimeoutǁ__init____mutmut_8, 
        'xǁTimeoutǁ__init____mutmut_9': xǁTimeoutǁ__init____mutmut_9, 
        'xǁTimeoutǁ__init____mutmut_10': xǁTimeoutǁ__init____mutmut_10, 
        'xǁTimeoutǁ__init____mutmut_11': xǁTimeoutǁ__init____mutmut_11, 
        'xǁTimeoutǁ__init____mutmut_12': xǁTimeoutǁ__init____mutmut_12, 
        'xǁTimeoutǁ__init____mutmut_13': xǁTimeoutǁ__init____mutmut_13, 
        'xǁTimeoutǁ__init____mutmut_14': xǁTimeoutǁ__init____mutmut_14, 
        'xǁTimeoutǁ__init____mutmut_15': xǁTimeoutǁ__init____mutmut_15, 
        'xǁTimeoutǁ__init____mutmut_16': xǁTimeoutǁ__init____mutmut_16, 
        'xǁTimeoutǁ__init____mutmut_17': xǁTimeoutǁ__init____mutmut_17
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTimeoutǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTimeoutǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTimeoutǁ__init____mutmut_orig)
    xǁTimeoutǁ__init____mutmut_orig.__name__ = 'xǁTimeoutǁ__init__'


class NetstringSocket:
    """
    Reads and writes using the netstring protocol.

    More info: https://en.wikipedia.org/wiki/Netstring
    Even more info: http://cr.yp.to/proto/netstrings.txt
    """
    def xǁNetstringSocketǁ__init____mutmut_orig(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_1(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = None
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_2(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(None)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_3(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = None
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_4(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = None
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_5(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = None  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_6(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) - 1  # len(str()) == log10
    def xǁNetstringSocketǁ__init____mutmut_7(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 2  # len(str()) == log10
    
    xǁNetstringSocketǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁ__init____mutmut_1': xǁNetstringSocketǁ__init____mutmut_1, 
        'xǁNetstringSocketǁ__init____mutmut_2': xǁNetstringSocketǁ__init____mutmut_2, 
        'xǁNetstringSocketǁ__init____mutmut_3': xǁNetstringSocketǁ__init____mutmut_3, 
        'xǁNetstringSocketǁ__init____mutmut_4': xǁNetstringSocketǁ__init____mutmut_4, 
        'xǁNetstringSocketǁ__init____mutmut_5': xǁNetstringSocketǁ__init____mutmut_5, 
        'xǁNetstringSocketǁ__init____mutmut_6': xǁNetstringSocketǁ__init____mutmut_6, 
        'xǁNetstringSocketǁ__init____mutmut_7': xǁNetstringSocketǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁNetstringSocketǁ__init____mutmut_orig)
    xǁNetstringSocketǁ__init____mutmut_orig.__name__ = 'xǁNetstringSocketǁ__init__'

    def fileno(self):
        return self.bsock.fileno()

    def xǁNetstringSocketǁsettimeout__mutmut_orig(self, timeout):
        self.timeout = timeout

    def xǁNetstringSocketǁsettimeout__mutmut_1(self, timeout):
        self.timeout = None
    
    xǁNetstringSocketǁsettimeout__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁsettimeout__mutmut_1': xǁNetstringSocketǁsettimeout__mutmut_1
    }
    
    def settimeout(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁsettimeout__mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁsettimeout__mutmut_mutants"), args, kwargs, self)
        return result 
    
    settimeout.__signature__ = _mutmut_signature(xǁNetstringSocketǁsettimeout__mutmut_orig)
    xǁNetstringSocketǁsettimeout__mutmut_orig.__name__ = 'xǁNetstringSocketǁsettimeout'

    def xǁNetstringSocketǁsetmaxsize__mutmut_orig(self, maxsize):
        self.maxsize = maxsize
        self._msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

    def xǁNetstringSocketǁsetmaxsize__mutmut_1(self, maxsize):
        self.maxsize = None
        self._msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

    def xǁNetstringSocketǁsetmaxsize__mutmut_2(self, maxsize):
        self.maxsize = maxsize
        self._msgsize_maxsize = None

    def xǁNetstringSocketǁsetmaxsize__mutmut_3(self, maxsize):
        self.maxsize = maxsize
        self._msgsize_maxsize = self._calc_msgsize_maxsize(None)
    
    xǁNetstringSocketǁsetmaxsize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁsetmaxsize__mutmut_1': xǁNetstringSocketǁsetmaxsize__mutmut_1, 
        'xǁNetstringSocketǁsetmaxsize__mutmut_2': xǁNetstringSocketǁsetmaxsize__mutmut_2, 
        'xǁNetstringSocketǁsetmaxsize__mutmut_3': xǁNetstringSocketǁsetmaxsize__mutmut_3
    }
    
    def setmaxsize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁsetmaxsize__mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁsetmaxsize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setmaxsize.__signature__ = _mutmut_signature(xǁNetstringSocketǁsetmaxsize__mutmut_orig)
    xǁNetstringSocketǁsetmaxsize__mutmut_orig.__name__ = 'xǁNetstringSocketǁsetmaxsize'

    def xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_orig(self, maxsize):
        return len(str(maxsize)) + 1  # len(str()) == log10

    def xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_1(self, maxsize):
        return len(str(maxsize)) - 1  # len(str()) == log10

    def xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_2(self, maxsize):
        return len(str(maxsize)) + 2  # len(str()) == log10
    
    xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_1': xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_1, 
        'xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_2': xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_2
    }
    
    def _calc_msgsize_maxsize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_msgsize_maxsize.__signature__ = _mutmut_signature(xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_orig)
    xǁNetstringSocketǁ_calc_msgsize_maxsize__mutmut_orig.__name__ = 'xǁNetstringSocketǁ_calc_msgsize_maxsize'

    def xǁNetstringSocketǁread_ns__mutmut_orig(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_1(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is not _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_2(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = None

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_3(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is not _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_4(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = None
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_5(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = None
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_6(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = None

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_7(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(None)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_8(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = None
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_9(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(None,
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_10(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=None,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_11(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=None)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_12(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_13(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_14(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            )
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_15(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b'XX:XX',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_16(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_17(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_18(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = None
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_19(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(None)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_20(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize(None)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_21(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' / size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_22(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('XXnetstring message size must be validXX'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_23(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('NETSTRING MESSAGE SIZE MUST BE VALID'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_24(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       'XX integer, not %rXX' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_25(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' INTEGER, NOT %R' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_26(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size >= maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_27(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(None, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_28(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, None)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_29(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_30(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, )
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_31(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = None
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_32(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(None)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_33(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(None) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_34(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(2) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_35(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) == b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_36(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b'XX,XX':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_37(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_38(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_39(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError(None)

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_40(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("XXexpected trailing ',' after messageXX")

        return payload

    def xǁNetstringSocketǁread_ns__mutmut_41(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        if maxsize is _UNSET:
            maxsize = self.maxsize
            msgsize_maxsize = self._msgsize_maxsize
        else:
            msgsize_maxsize = self._calc_msgsize_maxsize(maxsize)

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=timeout,
                                            maxsize=msgsize_maxsize)
        try:
            size = int(size_prefix)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_prefix)

        if size > maxsize:
            raise NetstringMessageTooLong(size, maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("EXPECTED TRAILING ',' AFTER MESSAGE")

        return payload
    
    xǁNetstringSocketǁread_ns__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁread_ns__mutmut_1': xǁNetstringSocketǁread_ns__mutmut_1, 
        'xǁNetstringSocketǁread_ns__mutmut_2': xǁNetstringSocketǁread_ns__mutmut_2, 
        'xǁNetstringSocketǁread_ns__mutmut_3': xǁNetstringSocketǁread_ns__mutmut_3, 
        'xǁNetstringSocketǁread_ns__mutmut_4': xǁNetstringSocketǁread_ns__mutmut_4, 
        'xǁNetstringSocketǁread_ns__mutmut_5': xǁNetstringSocketǁread_ns__mutmut_5, 
        'xǁNetstringSocketǁread_ns__mutmut_6': xǁNetstringSocketǁread_ns__mutmut_6, 
        'xǁNetstringSocketǁread_ns__mutmut_7': xǁNetstringSocketǁread_ns__mutmut_7, 
        'xǁNetstringSocketǁread_ns__mutmut_8': xǁNetstringSocketǁread_ns__mutmut_8, 
        'xǁNetstringSocketǁread_ns__mutmut_9': xǁNetstringSocketǁread_ns__mutmut_9, 
        'xǁNetstringSocketǁread_ns__mutmut_10': xǁNetstringSocketǁread_ns__mutmut_10, 
        'xǁNetstringSocketǁread_ns__mutmut_11': xǁNetstringSocketǁread_ns__mutmut_11, 
        'xǁNetstringSocketǁread_ns__mutmut_12': xǁNetstringSocketǁread_ns__mutmut_12, 
        'xǁNetstringSocketǁread_ns__mutmut_13': xǁNetstringSocketǁread_ns__mutmut_13, 
        'xǁNetstringSocketǁread_ns__mutmut_14': xǁNetstringSocketǁread_ns__mutmut_14, 
        'xǁNetstringSocketǁread_ns__mutmut_15': xǁNetstringSocketǁread_ns__mutmut_15, 
        'xǁNetstringSocketǁread_ns__mutmut_16': xǁNetstringSocketǁread_ns__mutmut_16, 
        'xǁNetstringSocketǁread_ns__mutmut_17': xǁNetstringSocketǁread_ns__mutmut_17, 
        'xǁNetstringSocketǁread_ns__mutmut_18': xǁNetstringSocketǁread_ns__mutmut_18, 
        'xǁNetstringSocketǁread_ns__mutmut_19': xǁNetstringSocketǁread_ns__mutmut_19, 
        'xǁNetstringSocketǁread_ns__mutmut_20': xǁNetstringSocketǁread_ns__mutmut_20, 
        'xǁNetstringSocketǁread_ns__mutmut_21': xǁNetstringSocketǁread_ns__mutmut_21, 
        'xǁNetstringSocketǁread_ns__mutmut_22': xǁNetstringSocketǁread_ns__mutmut_22, 
        'xǁNetstringSocketǁread_ns__mutmut_23': xǁNetstringSocketǁread_ns__mutmut_23, 
        'xǁNetstringSocketǁread_ns__mutmut_24': xǁNetstringSocketǁread_ns__mutmut_24, 
        'xǁNetstringSocketǁread_ns__mutmut_25': xǁNetstringSocketǁread_ns__mutmut_25, 
        'xǁNetstringSocketǁread_ns__mutmut_26': xǁNetstringSocketǁread_ns__mutmut_26, 
        'xǁNetstringSocketǁread_ns__mutmut_27': xǁNetstringSocketǁread_ns__mutmut_27, 
        'xǁNetstringSocketǁread_ns__mutmut_28': xǁNetstringSocketǁread_ns__mutmut_28, 
        'xǁNetstringSocketǁread_ns__mutmut_29': xǁNetstringSocketǁread_ns__mutmut_29, 
        'xǁNetstringSocketǁread_ns__mutmut_30': xǁNetstringSocketǁread_ns__mutmut_30, 
        'xǁNetstringSocketǁread_ns__mutmut_31': xǁNetstringSocketǁread_ns__mutmut_31, 
        'xǁNetstringSocketǁread_ns__mutmut_32': xǁNetstringSocketǁread_ns__mutmut_32, 
        'xǁNetstringSocketǁread_ns__mutmut_33': xǁNetstringSocketǁread_ns__mutmut_33, 
        'xǁNetstringSocketǁread_ns__mutmut_34': xǁNetstringSocketǁread_ns__mutmut_34, 
        'xǁNetstringSocketǁread_ns__mutmut_35': xǁNetstringSocketǁread_ns__mutmut_35, 
        'xǁNetstringSocketǁread_ns__mutmut_36': xǁNetstringSocketǁread_ns__mutmut_36, 
        'xǁNetstringSocketǁread_ns__mutmut_37': xǁNetstringSocketǁread_ns__mutmut_37, 
        'xǁNetstringSocketǁread_ns__mutmut_38': xǁNetstringSocketǁread_ns__mutmut_38, 
        'xǁNetstringSocketǁread_ns__mutmut_39': xǁNetstringSocketǁread_ns__mutmut_39, 
        'xǁNetstringSocketǁread_ns__mutmut_40': xǁNetstringSocketǁread_ns__mutmut_40, 
        'xǁNetstringSocketǁread_ns__mutmut_41': xǁNetstringSocketǁread_ns__mutmut_41
    }
    
    def read_ns(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁread_ns__mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁread_ns__mutmut_mutants"), args, kwargs, self)
        return result 
    
    read_ns.__signature__ = _mutmut_signature(xǁNetstringSocketǁread_ns__mutmut_orig)
    xǁNetstringSocketǁread_ns__mutmut_orig.__name__ = 'xǁNetstringSocketǁread_ns'

    def xǁNetstringSocketǁwrite_ns__mutmut_orig(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_1(self, payload):
        size = None
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_2(self, payload):
        size = len(payload)
        if size >= self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_3(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(None, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_4(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, None)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_5(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_6(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, )
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_7(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = None
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_8(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload - b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_9(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' - payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_10(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') - b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_11(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode(None) + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_12(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(None).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_13(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('XXasciiXX') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_14(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ASCII') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_15(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b'XX:XX' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_16(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_17(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_18(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b'XX,XX'
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_19(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_20(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)

    def xǁNetstringSocketǁwrite_ns__mutmut_21(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(None)
    
    xǁNetstringSocketǁwrite_ns__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringSocketǁwrite_ns__mutmut_1': xǁNetstringSocketǁwrite_ns__mutmut_1, 
        'xǁNetstringSocketǁwrite_ns__mutmut_2': xǁNetstringSocketǁwrite_ns__mutmut_2, 
        'xǁNetstringSocketǁwrite_ns__mutmut_3': xǁNetstringSocketǁwrite_ns__mutmut_3, 
        'xǁNetstringSocketǁwrite_ns__mutmut_4': xǁNetstringSocketǁwrite_ns__mutmut_4, 
        'xǁNetstringSocketǁwrite_ns__mutmut_5': xǁNetstringSocketǁwrite_ns__mutmut_5, 
        'xǁNetstringSocketǁwrite_ns__mutmut_6': xǁNetstringSocketǁwrite_ns__mutmut_6, 
        'xǁNetstringSocketǁwrite_ns__mutmut_7': xǁNetstringSocketǁwrite_ns__mutmut_7, 
        'xǁNetstringSocketǁwrite_ns__mutmut_8': xǁNetstringSocketǁwrite_ns__mutmut_8, 
        'xǁNetstringSocketǁwrite_ns__mutmut_9': xǁNetstringSocketǁwrite_ns__mutmut_9, 
        'xǁNetstringSocketǁwrite_ns__mutmut_10': xǁNetstringSocketǁwrite_ns__mutmut_10, 
        'xǁNetstringSocketǁwrite_ns__mutmut_11': xǁNetstringSocketǁwrite_ns__mutmut_11, 
        'xǁNetstringSocketǁwrite_ns__mutmut_12': xǁNetstringSocketǁwrite_ns__mutmut_12, 
        'xǁNetstringSocketǁwrite_ns__mutmut_13': xǁNetstringSocketǁwrite_ns__mutmut_13, 
        'xǁNetstringSocketǁwrite_ns__mutmut_14': xǁNetstringSocketǁwrite_ns__mutmut_14, 
        'xǁNetstringSocketǁwrite_ns__mutmut_15': xǁNetstringSocketǁwrite_ns__mutmut_15, 
        'xǁNetstringSocketǁwrite_ns__mutmut_16': xǁNetstringSocketǁwrite_ns__mutmut_16, 
        'xǁNetstringSocketǁwrite_ns__mutmut_17': xǁNetstringSocketǁwrite_ns__mutmut_17, 
        'xǁNetstringSocketǁwrite_ns__mutmut_18': xǁNetstringSocketǁwrite_ns__mutmut_18, 
        'xǁNetstringSocketǁwrite_ns__mutmut_19': xǁNetstringSocketǁwrite_ns__mutmut_19, 
        'xǁNetstringSocketǁwrite_ns__mutmut_20': xǁNetstringSocketǁwrite_ns__mutmut_20, 
        'xǁNetstringSocketǁwrite_ns__mutmut_21': xǁNetstringSocketǁwrite_ns__mutmut_21
    }
    
    def write_ns(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringSocketǁwrite_ns__mutmut_orig"), object.__getattribute__(self, "xǁNetstringSocketǁwrite_ns__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write_ns.__signature__ = _mutmut_signature(xǁNetstringSocketǁwrite_ns__mutmut_orig)
    xǁNetstringSocketǁwrite_ns__mutmut_orig.__name__ = 'xǁNetstringSocketǁwrite_ns'


class NetstringProtocolError(Error):
    "Base class for all of socketutils' Netstring exception types."
    pass


class NetstringInvalidSize(NetstringProtocolError):
    """NetstringInvalidSize is raised when the ``:``-delimited size prefix
    of the message does not contain a valid integer.

    Message showing valid size::

      5:hello,

    Here the ``5`` is the size. Anything in this prefix position that
    is not parsable as a Python integer (i.e., :class:`int`) will raise
    this exception.
    """
    def xǁNetstringInvalidSizeǁ__init____mutmut_orig(self, msg):
        super().__init__(msg)
    def xǁNetstringInvalidSizeǁ__init____mutmut_1(self, msg):
        super().__init__(None)
    
    xǁNetstringInvalidSizeǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringInvalidSizeǁ__init____mutmut_1': xǁNetstringInvalidSizeǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringInvalidSizeǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNetstringInvalidSizeǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁNetstringInvalidSizeǁ__init____mutmut_orig)
    xǁNetstringInvalidSizeǁ__init____mutmut_orig.__name__ = 'xǁNetstringInvalidSizeǁ__init__'


class NetstringMessageTooLong(NetstringProtocolError):
    """NetstringMessageTooLong is raised when the size prefix contains a
    valid integer, but that integer is larger than the
    :class:`NetstringSocket`'s configured *maxsize*.

    When this exception is raised, it's recommended to simply close
    the connection instead of trying to recover.
    """
    def xǁNetstringMessageTooLongǁ__init____mutmut_orig(self, size, maxsize):
        msg = ('netstring message length exceeds configured maxsize: %s > %s'
               % (size, maxsize))
        super().__init__(msg)
    def xǁNetstringMessageTooLongǁ__init____mutmut_1(self, size, maxsize):
        msg = None
        super().__init__(msg)
    def xǁNetstringMessageTooLongǁ__init____mutmut_2(self, size, maxsize):
        msg = ('netstring message length exceeds configured maxsize: %s > %s' / (size, maxsize))
        super().__init__(msg)
    def xǁNetstringMessageTooLongǁ__init____mutmut_3(self, size, maxsize):
        msg = ('XXnetstring message length exceeds configured maxsize: %s > %sXX'
               % (size, maxsize))
        super().__init__(msg)
    def xǁNetstringMessageTooLongǁ__init____mutmut_4(self, size, maxsize):
        msg = ('NETSTRING MESSAGE LENGTH EXCEEDS CONFIGURED MAXSIZE: %S > %S'
               % (size, maxsize))
        super().__init__(msg)
    def xǁNetstringMessageTooLongǁ__init____mutmut_5(self, size, maxsize):
        msg = ('netstring message length exceeds configured maxsize: %s > %s'
               % (size, maxsize))
        super().__init__(None)
    
    xǁNetstringMessageTooLongǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNetstringMessageTooLongǁ__init____mutmut_1': xǁNetstringMessageTooLongǁ__init____mutmut_1, 
        'xǁNetstringMessageTooLongǁ__init____mutmut_2': xǁNetstringMessageTooLongǁ__init____mutmut_2, 
        'xǁNetstringMessageTooLongǁ__init____mutmut_3': xǁNetstringMessageTooLongǁ__init____mutmut_3, 
        'xǁNetstringMessageTooLongǁ__init____mutmut_4': xǁNetstringMessageTooLongǁ__init____mutmut_4, 
        'xǁNetstringMessageTooLongǁ__init____mutmut_5': xǁNetstringMessageTooLongǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNetstringMessageTooLongǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNetstringMessageTooLongǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁNetstringMessageTooLongǁ__init____mutmut_orig)
    xǁNetstringMessageTooLongǁ__init____mutmut_orig.__name__ = 'xǁNetstringMessageTooLongǁ__init__'


"""
attrs worth adding/passing through:


properties: type, proto

For its main functionality, BufferedSocket can wrap any object that
has the following methods:

  - gettimeout()
  - settimeout()
  - recv(size)
  - send(data)

The following methods are passed through:

...

"""

# TODO: buffered socket check socket.type == SOCK_STREAM?
# TODO: make recv_until support taking a regex
# TODO: including the delimiter in the recv_until return is not
#       necessary, as ConnectionClosed differentiates empty messages
#       from socket closes.
