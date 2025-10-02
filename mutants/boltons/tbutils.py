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

"""One of the oft-cited tenets of Python is that it is better to ask
forgiveness than permission. That is, there are many cases where it is
more inclusive and correct to handle exceptions than spend extra lines
and execution time checking for conditions. This philosophy makes good
exception handling features all the more important. Unfortunately
Python's :mod:`traceback` module is woefully behind the times.

The ``tbutils`` module provides two disparate but complementary featuresets:

  1. With :class:`ExceptionInfo` and :class:`TracebackInfo`, the
     ability to extract, construct, manipulate, format, and serialize
     exceptions, tracebacks, and callstacks.
  2. With :class:`ParsedException`, the ability to find and parse tracebacks
     from captured output such as logs and stdout.

There is also the :class:`ContextualTracebackInfo` variant of
:class:`TracebackInfo`, which includes much more information from each
frame of the callstack, including values of locals and neighboring
lines of code.
"""


import re
import sys
import linecache


# TODO: chaining primitives?  what are real use cases where these help?

# TODO: print_* for backwards compatibility
# __all__ = ['extract_stack', 'extract_tb', 'format_exception',
#            'format_exception_only', 'format_list', 'format_stack',
#            'format_tb', 'print_exc', 'format_exc', 'print_exception',
#            'print_last', 'print_stack', 'print_tb']


__all__ = ['ExceptionInfo', 'TracebackInfo', 'Callpoint',
           'ContextualExceptionInfo', 'ContextualTracebackInfo',
           'ContextualCallpoint', 'print_exception', 'ParsedException']
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


class Callpoint:
    """The Callpoint is a lightweight object used to represent a single
    entry in the code of a call stack. It stores the code-related
    metadata of a given frame. Available attributes are the same as
    the parameters below.

    Args:
        func_name (str): the function name
        lineno (int): the line number
        module_name (str): the module name
        module_path (str): the filesystem path of the module
        lasti (int): the index of bytecode execution
        line (str): the single-line code content (if available)

    """
    __slots__ = ('func_name', 'lineno', 'module_name', 'module_path', 'lasti',
                 'line')

    def xǁCallpointǁ__init____mutmut_orig(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def xǁCallpointǁ__init____mutmut_1(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = None
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def xǁCallpointǁ__init____mutmut_2(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = None
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def xǁCallpointǁ__init____mutmut_3(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = None
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def xǁCallpointǁ__init____mutmut_4(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = None
        self.lasti = lasti
        self.line = line

    def xǁCallpointǁ__init____mutmut_5(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = None
        self.line = line

    def xǁCallpointǁ__init____mutmut_6(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = None
    
    xǁCallpointǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCallpointǁ__init____mutmut_1': xǁCallpointǁ__init____mutmut_1, 
        'xǁCallpointǁ__init____mutmut_2': xǁCallpointǁ__init____mutmut_2, 
        'xǁCallpointǁ__init____mutmut_3': xǁCallpointǁ__init____mutmut_3, 
        'xǁCallpointǁ__init____mutmut_4': xǁCallpointǁ__init____mutmut_4, 
        'xǁCallpointǁ__init____mutmut_5': xǁCallpointǁ__init____mutmut_5, 
        'xǁCallpointǁ__init____mutmut_6': xǁCallpointǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCallpointǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCallpointǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCallpointǁ__init____mutmut_orig)
    xǁCallpointǁ__init____mutmut_orig.__name__ = 'xǁCallpointǁ__init__'

    def xǁCallpointǁto_dict__mutmut_orig(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_1(self):
        "XXGet a :class:`dict` copy of the Callpoint. Useful for serialization.XX"
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_2(self):
        "get a :class:`dict` copy of the callpoint. useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_3(self):
        "GET A :CLASS:`DICT` COPY OF THE CALLPOINT. USEFUL FOR SERIALIZATION."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_4(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = None
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_5(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = None
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_6(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(None, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_7(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, None)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_8(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_9(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, )
            except AttributeError:
                pass
            else:
                ret[slot] = str(val) if isinstance(val, _DeferredLine) else val
        return ret

    def xǁCallpointǁto_dict__mutmut_10(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = None
        return ret

    def xǁCallpointǁto_dict__mutmut_11(self):
        "Get a :class:`dict` copy of the Callpoint. Useful for serialization."
        ret = {}
        for slot in self.__slots__:
            try:
                val = getattr(self, slot)
            except AttributeError:
                pass
            else:
                ret[slot] = str(None) if isinstance(val, _DeferredLine) else val
        return ret
    
    xǁCallpointǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCallpointǁto_dict__mutmut_1': xǁCallpointǁto_dict__mutmut_1, 
        'xǁCallpointǁto_dict__mutmut_2': xǁCallpointǁto_dict__mutmut_2, 
        'xǁCallpointǁto_dict__mutmut_3': xǁCallpointǁto_dict__mutmut_3, 
        'xǁCallpointǁto_dict__mutmut_4': xǁCallpointǁto_dict__mutmut_4, 
        'xǁCallpointǁto_dict__mutmut_5': xǁCallpointǁto_dict__mutmut_5, 
        'xǁCallpointǁto_dict__mutmut_6': xǁCallpointǁto_dict__mutmut_6, 
        'xǁCallpointǁto_dict__mutmut_7': xǁCallpointǁto_dict__mutmut_7, 
        'xǁCallpointǁto_dict__mutmut_8': xǁCallpointǁto_dict__mutmut_8, 
        'xǁCallpointǁto_dict__mutmut_9': xǁCallpointǁto_dict__mutmut_9, 
        'xǁCallpointǁto_dict__mutmut_10': xǁCallpointǁto_dict__mutmut_10, 
        'xǁCallpointǁto_dict__mutmut_11': xǁCallpointǁto_dict__mutmut_11
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCallpointǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁCallpointǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁCallpointǁto_dict__mutmut_orig)
    xǁCallpointǁto_dict__mutmut_orig.__name__ = 'xǁCallpointǁto_dict'

    @classmethod
    def from_current(cls, level=1):
        "Creates a Callpoint from the location of the calling function."
        frame = sys._getframe(level)
        return cls.from_frame(frame)

    @classmethod
    def from_frame(cls, frame):
        "Create a Callpoint object from data extracted from the given frame."
        func_name = frame.f_code.co_name
        lineno = frame.f_lineno
        module_name = frame.f_globals.get('__name__', '')
        module_path = frame.f_code.co_filename
        lasti = frame.f_lasti
        line = _DeferredLine(module_path, lineno, frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    @classmethod
    def from_tb(cls, tb):
        """Create a Callpoint from the traceback of the current
        exception. Main difference with :meth:`from_frame` is that
        ``lineno`` and ``lasti`` come from the traceback, which is to
        say the line that failed in the try block, not the line
        currently being executed (in the except block).
        """
        func_name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        lasti = tb.tb_lasti
        module_name = tb.tb_frame.f_globals.get('__name__', '')
        module_path = tb.tb_frame.f_code.co_filename
        line = _DeferredLine(module_path, lineno, tb.tb_frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    def xǁCallpointǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_1(self):
        cn = None
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        args = None
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        args = [getattr(None, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        args = [getattr(self, None, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        args = [getattr(s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        args = [getattr(self, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_7(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, ) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_8(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_9(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(None):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_10(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(None, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_11(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, None)

    def xǁCallpointǁ__repr____mutmut_12(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_13(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, )

    def xǁCallpointǁ__repr____mutmut_14(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return 'XX{}({})XX'.format(cn, ', '.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_15(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join(None))

    def xǁCallpointǁ__repr____mutmut_16(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, 'XX, XX'.join([repr(a) for a in args]))

    def xǁCallpointǁ__repr____mutmut_17(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super().__repr__()
        else:
            return '{}({})'.format(cn, ', '.join([repr(None) for a in args]))
    
    xǁCallpointǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCallpointǁ__repr____mutmut_1': xǁCallpointǁ__repr____mutmut_1, 
        'xǁCallpointǁ__repr____mutmut_2': xǁCallpointǁ__repr____mutmut_2, 
        'xǁCallpointǁ__repr____mutmut_3': xǁCallpointǁ__repr____mutmut_3, 
        'xǁCallpointǁ__repr____mutmut_4': xǁCallpointǁ__repr____mutmut_4, 
        'xǁCallpointǁ__repr____mutmut_5': xǁCallpointǁ__repr____mutmut_5, 
        'xǁCallpointǁ__repr____mutmut_6': xǁCallpointǁ__repr____mutmut_6, 
        'xǁCallpointǁ__repr____mutmut_7': xǁCallpointǁ__repr____mutmut_7, 
        'xǁCallpointǁ__repr____mutmut_8': xǁCallpointǁ__repr____mutmut_8, 
        'xǁCallpointǁ__repr____mutmut_9': xǁCallpointǁ__repr____mutmut_9, 
        'xǁCallpointǁ__repr____mutmut_10': xǁCallpointǁ__repr____mutmut_10, 
        'xǁCallpointǁ__repr____mutmut_11': xǁCallpointǁ__repr____mutmut_11, 
        'xǁCallpointǁ__repr____mutmut_12': xǁCallpointǁ__repr____mutmut_12, 
        'xǁCallpointǁ__repr____mutmut_13': xǁCallpointǁ__repr____mutmut_13, 
        'xǁCallpointǁ__repr____mutmut_14': xǁCallpointǁ__repr____mutmut_14, 
        'xǁCallpointǁ__repr____mutmut_15': xǁCallpointǁ__repr____mutmut_15, 
        'xǁCallpointǁ__repr____mutmut_16': xǁCallpointǁ__repr____mutmut_16, 
        'xǁCallpointǁ__repr____mutmut_17': xǁCallpointǁ__repr____mutmut_17
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCallpointǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁCallpointǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁCallpointǁ__repr____mutmut_orig)
    xǁCallpointǁ__repr____mutmut_orig.__name__ = 'xǁCallpointǁ__repr__'

    def xǁCallpointǁtb_frame_str__mutmut_orig(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_1(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = None
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_2(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(None,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_3(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 None,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_4(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 None)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_5(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_6(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_7(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 )
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_8(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = 'XX  File "{}", line {}, in {}\nXX'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_9(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  file "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_10(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  FILE "{}", LINE {}, IN {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_11(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret = f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_12(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret -= f'    {str(self.line).strip()}\n'
        return ret

    def xǁCallpointǁtb_frame_str__mutmut_13(self):
        """Render the Callpoint as it would appear in a standard printed
        Python traceback. Returns a string with filename, line number,
        function name, and the actual code line of the error on up to
        two lines.
        """
        ret = '  File "{}", line {}, in {}\n'.format(self.module_path,
                                                 self.lineno,
                                                 self.func_name)
        if self.line:
            ret += f'    {str(None).strip()}\n'
        return ret
    
    xǁCallpointǁtb_frame_str__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCallpointǁtb_frame_str__mutmut_1': xǁCallpointǁtb_frame_str__mutmut_1, 
        'xǁCallpointǁtb_frame_str__mutmut_2': xǁCallpointǁtb_frame_str__mutmut_2, 
        'xǁCallpointǁtb_frame_str__mutmut_3': xǁCallpointǁtb_frame_str__mutmut_3, 
        'xǁCallpointǁtb_frame_str__mutmut_4': xǁCallpointǁtb_frame_str__mutmut_4, 
        'xǁCallpointǁtb_frame_str__mutmut_5': xǁCallpointǁtb_frame_str__mutmut_5, 
        'xǁCallpointǁtb_frame_str__mutmut_6': xǁCallpointǁtb_frame_str__mutmut_6, 
        'xǁCallpointǁtb_frame_str__mutmut_7': xǁCallpointǁtb_frame_str__mutmut_7, 
        'xǁCallpointǁtb_frame_str__mutmut_8': xǁCallpointǁtb_frame_str__mutmut_8, 
        'xǁCallpointǁtb_frame_str__mutmut_9': xǁCallpointǁtb_frame_str__mutmut_9, 
        'xǁCallpointǁtb_frame_str__mutmut_10': xǁCallpointǁtb_frame_str__mutmut_10, 
        'xǁCallpointǁtb_frame_str__mutmut_11': xǁCallpointǁtb_frame_str__mutmut_11, 
        'xǁCallpointǁtb_frame_str__mutmut_12': xǁCallpointǁtb_frame_str__mutmut_12, 
        'xǁCallpointǁtb_frame_str__mutmut_13': xǁCallpointǁtb_frame_str__mutmut_13
    }
    
    def tb_frame_str(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCallpointǁtb_frame_str__mutmut_orig"), object.__getattribute__(self, "xǁCallpointǁtb_frame_str__mutmut_mutants"), args, kwargs, self)
        return result 
    
    tb_frame_str.__signature__ = _mutmut_signature(xǁCallpointǁtb_frame_str__mutmut_orig)
    xǁCallpointǁtb_frame_str__mutmut_orig.__name__ = 'xǁCallpointǁtb_frame_str'


class _DeferredLine:
    """The _DeferredLine type allows Callpoints and TracebackInfos to be
    constructed without potentially hitting the filesystem, as is the
    normal behavior of the standard Python :mod:`traceback` and
    :mod:`linecache` modules. Calling :func:`str` fetches and caches
    the line.

    Args:
        filename (str): the path of the file containing the line
        lineno (int): the number of the line in question
        module_globals (dict): an optional dict of module globals,
            used to handle advanced use cases using custom module loaders.

    """
    __slots__ = ('filename', 'lineno', '_line', '_mod_name', '_mod_loader')

    def xǁ_DeferredLineǁ__init____mutmut_orig(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_1(self, filename, lineno, module_globals=None):
        self.filename = None
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_2(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = None
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_3(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is not None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_4(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = ""
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_5(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = ""
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_6(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = None
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_7(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get(None)
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_8(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('XX__name__XX')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_9(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__NAME__')
            self._mod_loader = module_globals.get('__loader__')

    def xǁ_DeferredLineǁ__init____mutmut_10(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = None

    def xǁ_DeferredLineǁ__init____mutmut_11(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get(None)

    def xǁ_DeferredLineǁ__init____mutmut_12(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('XX__loader__XX')

    def xǁ_DeferredLineǁ__init____mutmut_13(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        if module_globals is None:
            self._mod_name = None
            self._mod_loader = None
        else:
            self._mod_name = module_globals.get('__name__')
            self._mod_loader = module_globals.get('__LOADER__')
    
    xǁ_DeferredLineǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_DeferredLineǁ__init____mutmut_1': xǁ_DeferredLineǁ__init____mutmut_1, 
        'xǁ_DeferredLineǁ__init____mutmut_2': xǁ_DeferredLineǁ__init____mutmut_2, 
        'xǁ_DeferredLineǁ__init____mutmut_3': xǁ_DeferredLineǁ__init____mutmut_3, 
        'xǁ_DeferredLineǁ__init____mutmut_4': xǁ_DeferredLineǁ__init____mutmut_4, 
        'xǁ_DeferredLineǁ__init____mutmut_5': xǁ_DeferredLineǁ__init____mutmut_5, 
        'xǁ_DeferredLineǁ__init____mutmut_6': xǁ_DeferredLineǁ__init____mutmut_6, 
        'xǁ_DeferredLineǁ__init____mutmut_7': xǁ_DeferredLineǁ__init____mutmut_7, 
        'xǁ_DeferredLineǁ__init____mutmut_8': xǁ_DeferredLineǁ__init____mutmut_8, 
        'xǁ_DeferredLineǁ__init____mutmut_9': xǁ_DeferredLineǁ__init____mutmut_9, 
        'xǁ_DeferredLineǁ__init____mutmut_10': xǁ_DeferredLineǁ__init____mutmut_10, 
        'xǁ_DeferredLineǁ__init____mutmut_11': xǁ_DeferredLineǁ__init____mutmut_11, 
        'xǁ_DeferredLineǁ__init____mutmut_12': xǁ_DeferredLineǁ__init____mutmut_12, 
        'xǁ_DeferredLineǁ__init____mutmut_13': xǁ_DeferredLineǁ__init____mutmut_13
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_DeferredLineǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁ_DeferredLineǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁ_DeferredLineǁ__init____mutmut_orig)
    xǁ_DeferredLineǁ__init____mutmut_orig.__name__ = 'xǁ_DeferredLineǁ__init__'

    def xǁ_DeferredLineǁ__eq____mutmut_orig(self, other):
        return (self.lineno, self.filename) == (other.lineno, other.filename)

    def xǁ_DeferredLineǁ__eq____mutmut_1(self, other):
        return (self.lineno, self.filename) != (other.lineno, other.filename)
    
    xǁ_DeferredLineǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_DeferredLineǁ__eq____mutmut_1': xǁ_DeferredLineǁ__eq____mutmut_1
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_DeferredLineǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁ_DeferredLineǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁ_DeferredLineǁ__eq____mutmut_orig)
    xǁ_DeferredLineǁ__eq____mutmut_orig.__name__ = 'xǁ_DeferredLineǁ__eq__'

    def xǁ_DeferredLineǁ__ne____mutmut_orig(self, other):
        return not self == other

    def xǁ_DeferredLineǁ__ne____mutmut_1(self, other):
        return self == other

    def xǁ_DeferredLineǁ__ne____mutmut_2(self, other):
        return not self != other
    
    xǁ_DeferredLineǁ__ne____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_DeferredLineǁ__ne____mutmut_1': xǁ_DeferredLineǁ__ne____mutmut_1, 
        'xǁ_DeferredLineǁ__ne____mutmut_2': xǁ_DeferredLineǁ__ne____mutmut_2
    }
    
    def __ne__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_DeferredLineǁ__ne____mutmut_orig"), object.__getattribute__(self, "xǁ_DeferredLineǁ__ne____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ne__.__signature__ = _mutmut_signature(xǁ_DeferredLineǁ__ne____mutmut_orig)
    xǁ_DeferredLineǁ__ne____mutmut_orig.__name__ = 'xǁ_DeferredLineǁ__ne__'

    def xǁ_DeferredLineǁ__str____mutmut_orig(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_1(self):
        ret = None
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_2(self):
        ret = getattr(None, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_3(self):
        ret = getattr(self, None, None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_4(self):
        ret = getattr('_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_5(self):
        ret = getattr(self, None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_6(self):
        ret = getattr(self, '_line', )
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_7(self):
        ret = getattr(self, 'XX_lineXX', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_8(self):
        ret = getattr(self, '_LINE', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_9(self):
        ret = getattr(self, '_line', None)
        if ret is None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_10(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(None)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_11(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = None
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_12(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'XX__name__XX': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_13(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__NAME__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_14(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           'XX__loader__XX': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_15(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__LOADER__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_16(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = None
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_17(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(None,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_18(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     None,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_19(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     None)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_20(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_21(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_22(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     )
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_23(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = None
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_24(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.lstrip()
        except KeyError:
            line = ''
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_25(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = None
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_26(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = 'XXXX'
        self._line = line
        return line

    def xǁ_DeferredLineǁ__str____mutmut_27(self):
        ret = getattr(self, '_line', None)
        if ret is not None:
            return ret
        try:
            linecache.checkcache(self.filename)
            mod_globals = {'__name__': self._mod_name,
                           '__loader__': self._mod_loader}
            line = linecache.getline(self.filename,
                                     self.lineno,
                                     mod_globals)
            line = line.rstrip()
        except KeyError:
            line = ''
        self._line = None
        return line
    
    xǁ_DeferredLineǁ__str____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_DeferredLineǁ__str____mutmut_1': xǁ_DeferredLineǁ__str____mutmut_1, 
        'xǁ_DeferredLineǁ__str____mutmut_2': xǁ_DeferredLineǁ__str____mutmut_2, 
        'xǁ_DeferredLineǁ__str____mutmut_3': xǁ_DeferredLineǁ__str____mutmut_3, 
        'xǁ_DeferredLineǁ__str____mutmut_4': xǁ_DeferredLineǁ__str____mutmut_4, 
        'xǁ_DeferredLineǁ__str____mutmut_5': xǁ_DeferredLineǁ__str____mutmut_5, 
        'xǁ_DeferredLineǁ__str____mutmut_6': xǁ_DeferredLineǁ__str____mutmut_6, 
        'xǁ_DeferredLineǁ__str____mutmut_7': xǁ_DeferredLineǁ__str____mutmut_7, 
        'xǁ_DeferredLineǁ__str____mutmut_8': xǁ_DeferredLineǁ__str____mutmut_8, 
        'xǁ_DeferredLineǁ__str____mutmut_9': xǁ_DeferredLineǁ__str____mutmut_9, 
        'xǁ_DeferredLineǁ__str____mutmut_10': xǁ_DeferredLineǁ__str____mutmut_10, 
        'xǁ_DeferredLineǁ__str____mutmut_11': xǁ_DeferredLineǁ__str____mutmut_11, 
        'xǁ_DeferredLineǁ__str____mutmut_12': xǁ_DeferredLineǁ__str____mutmut_12, 
        'xǁ_DeferredLineǁ__str____mutmut_13': xǁ_DeferredLineǁ__str____mutmut_13, 
        'xǁ_DeferredLineǁ__str____mutmut_14': xǁ_DeferredLineǁ__str____mutmut_14, 
        'xǁ_DeferredLineǁ__str____mutmut_15': xǁ_DeferredLineǁ__str____mutmut_15, 
        'xǁ_DeferredLineǁ__str____mutmut_16': xǁ_DeferredLineǁ__str____mutmut_16, 
        'xǁ_DeferredLineǁ__str____mutmut_17': xǁ_DeferredLineǁ__str____mutmut_17, 
        'xǁ_DeferredLineǁ__str____mutmut_18': xǁ_DeferredLineǁ__str____mutmut_18, 
        'xǁ_DeferredLineǁ__str____mutmut_19': xǁ_DeferredLineǁ__str____mutmut_19, 
        'xǁ_DeferredLineǁ__str____mutmut_20': xǁ_DeferredLineǁ__str____mutmut_20, 
        'xǁ_DeferredLineǁ__str____mutmut_21': xǁ_DeferredLineǁ__str____mutmut_21, 
        'xǁ_DeferredLineǁ__str____mutmut_22': xǁ_DeferredLineǁ__str____mutmut_22, 
        'xǁ_DeferredLineǁ__str____mutmut_23': xǁ_DeferredLineǁ__str____mutmut_23, 
        'xǁ_DeferredLineǁ__str____mutmut_24': xǁ_DeferredLineǁ__str____mutmut_24, 
        'xǁ_DeferredLineǁ__str____mutmut_25': xǁ_DeferredLineǁ__str____mutmut_25, 
        'xǁ_DeferredLineǁ__str____mutmut_26': xǁ_DeferredLineǁ__str____mutmut_26, 
        'xǁ_DeferredLineǁ__str____mutmut_27': xǁ_DeferredLineǁ__str____mutmut_27
    }
    
    def __str__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_DeferredLineǁ__str____mutmut_orig"), object.__getattribute__(self, "xǁ_DeferredLineǁ__str____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __str__.__signature__ = _mutmut_signature(xǁ_DeferredLineǁ__str____mutmut_orig)
    xǁ_DeferredLineǁ__str____mutmut_orig.__name__ = 'xǁ_DeferredLineǁ__str__'

    def xǁ_DeferredLineǁ__repr____mutmut_orig(self):
        return repr(str(self))

    def xǁ_DeferredLineǁ__repr____mutmut_1(self):
        return repr(None)

    def xǁ_DeferredLineǁ__repr____mutmut_2(self):
        return repr(str(None))
    
    xǁ_DeferredLineǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_DeferredLineǁ__repr____mutmut_1': xǁ_DeferredLineǁ__repr____mutmut_1, 
        'xǁ_DeferredLineǁ__repr____mutmut_2': xǁ_DeferredLineǁ__repr____mutmut_2
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_DeferredLineǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁ_DeferredLineǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁ_DeferredLineǁ__repr____mutmut_orig)
    xǁ_DeferredLineǁ__repr____mutmut_orig.__name__ = 'xǁ_DeferredLineǁ__repr__'

    def __len__(self):
        return len(str(self))


# TODO: dedup frames, look at __eq__ on _DeferredLine
class TracebackInfo:
    """The TracebackInfo class provides a basic representation of a stack
    trace, be it from an exception being handled or just part of
    normal execution. It is basically a wrapper around a list of
    :class:`Callpoint` objects representing frames.

    Args:
        frames (list): A list of frame objects in the stack.

    .. note ::

      ``TracebackInfo`` can represent both exception tracebacks and
      non-exception tracebacks (aka stack traces). As a result, there
      is no ``TracebackInfo.from_current()``, as that would be
      ambiguous. Instead, call :meth:`TracebackInfo.from_frame`
      without the *frame* argument for a stack trace, or
      :meth:`TracebackInfo.from_traceback` without the *tb* argument
      for an exception traceback.
    """
    callpoint_type = Callpoint

    def xǁTracebackInfoǁ__init____mutmut_orig(self, frames):
        self.frames = frames

    def xǁTracebackInfoǁ__init____mutmut_1(self, frames):
        self.frames = None
    
    xǁTracebackInfoǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracebackInfoǁ__init____mutmut_1': xǁTracebackInfoǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracebackInfoǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTracebackInfoǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTracebackInfoǁ__init____mutmut_orig)
    xǁTracebackInfoǁ__init____mutmut_orig.__name__ = 'xǁTracebackInfoǁ__init__'

    @classmethod
    def from_frame(cls, frame=None, level=1, limit=None):
        """Create a new TracebackInfo *frame* by recurring up in the stack a
        max of *limit* times. If *frame* is unset, get the frame from
        :func:`sys._getframe` using *level*.

        Args:
            frame (types.FrameType): frame object from
                :func:`sys._getframe` or elsewhere. Defaults to result
                of :func:`sys.get_frame`.
            level (int): If *frame* is unset, the desired frame is
                this many levels up the stack from the invocation of
                this method. Default ``1`` (i.e., caller of this method).
            limit (int): max number of parent frames to extract
                (defaults to :data:`sys.tracebacklimit`)

        """
        ret = []
        if frame is None:
            frame = sys._getframe(level)
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while frame is not None and n < limit:
            item = cls.callpoint_type.from_frame(frame)
            ret.append(item)
            frame = frame.f_back
            n += 1
        ret.reverse()
        return cls(ret)

    @classmethod
    def from_traceback(cls, tb=None, limit=None):
        """Create a new TracebackInfo from the traceback *tb* by recurring
        up in the stack a max of *limit* times. If *tb* is unset, get
        the traceback from the currently handled exception. If no
        exception is being handled, raise a :exc:`ValueError`.

        Args:

            frame (types.TracebackType): traceback object from
                :func:`sys.exc_info` or elsewhere. If absent or set to
                ``None``, defaults to ``sys.exc_info()[2]``, and
                raises a :exc:`ValueError` if no exception is
                currently being handled.
            limit (int): max number of parent frames to extract
                (defaults to :data:`sys.tracebacklimit`)

        """
        ret = []
        if tb is None:
            tb = sys.exc_info()[2]
            if tb is None:
                raise ValueError('no tb set and no exception being handled')
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while tb is not None and n < limit:
            item = cls.callpoint_type.from_tb(tb)
            ret.append(item)
            tb = tb.tb_next
            n += 1
        return cls(ret)

    @classmethod
    def from_dict(cls, d):
        "Complements :meth:`TracebackInfo.to_dict`."
        # TODO: check this.
        return cls(d['frames'])

    def xǁTracebackInfoǁto_dict__mutmut_orig(self):
        """Returns a dict with a list of :class:`Callpoint` frames converted
        to dicts.
        """
        return {'frames': [f.to_dict() for f in self.frames]}

    def xǁTracebackInfoǁto_dict__mutmut_1(self):
        """Returns a dict with a list of :class:`Callpoint` frames converted
        to dicts.
        """
        return {'XXframesXX': [f.to_dict() for f in self.frames]}

    def xǁTracebackInfoǁto_dict__mutmut_2(self):
        """Returns a dict with a list of :class:`Callpoint` frames converted
        to dicts.
        """
        return {'FRAMES': [f.to_dict() for f in self.frames]}
    
    xǁTracebackInfoǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracebackInfoǁto_dict__mutmut_1': xǁTracebackInfoǁto_dict__mutmut_1, 
        'xǁTracebackInfoǁto_dict__mutmut_2': xǁTracebackInfoǁto_dict__mutmut_2
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracebackInfoǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁTracebackInfoǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁTracebackInfoǁto_dict__mutmut_orig)
    xǁTracebackInfoǁto_dict__mutmut_orig.__name__ = 'xǁTracebackInfoǁto_dict'

    def __len__(self):
        return len(self.frames)

    def xǁTracebackInfoǁ__iter____mutmut_orig(self):
        return iter(self.frames)

    def xǁTracebackInfoǁ__iter____mutmut_1(self):
        return iter(None)
    
    xǁTracebackInfoǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracebackInfoǁ__iter____mutmut_1': xǁTracebackInfoǁ__iter____mutmut_1
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracebackInfoǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁTracebackInfoǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁTracebackInfoǁ__iter____mutmut_orig)
    xǁTracebackInfoǁ__iter____mutmut_orig.__name__ = 'xǁTracebackInfoǁ__iter__'

    def xǁTracebackInfoǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[-1]!r}'
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_1(self):
        cn = None

        if self.frames:
            frame_part = f' last={self.frames[-1]!r}'
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = None
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[+1]!r}'
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[-2]!r}'
        else:
            frame_part = ''

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[-1]!r}'
        else:
            frame_part = None

        return f'<{cn} frames={len(self.frames)}{frame_part}>'

    def xǁTracebackInfoǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__

        if self.frames:
            frame_part = f' last={self.frames[-1]!r}'
        else:
            frame_part = 'XXXX'

        return f'<{cn} frames={len(self.frames)}{frame_part}>'
    
    xǁTracebackInfoǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracebackInfoǁ__repr____mutmut_1': xǁTracebackInfoǁ__repr____mutmut_1, 
        'xǁTracebackInfoǁ__repr____mutmut_2': xǁTracebackInfoǁ__repr____mutmut_2, 
        'xǁTracebackInfoǁ__repr____mutmut_3': xǁTracebackInfoǁ__repr____mutmut_3, 
        'xǁTracebackInfoǁ__repr____mutmut_4': xǁTracebackInfoǁ__repr____mutmut_4, 
        'xǁTracebackInfoǁ__repr____mutmut_5': xǁTracebackInfoǁ__repr____mutmut_5, 
        'xǁTracebackInfoǁ__repr____mutmut_6': xǁTracebackInfoǁ__repr____mutmut_6
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracebackInfoǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁTracebackInfoǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁTracebackInfoǁ__repr____mutmut_orig)
    xǁTracebackInfoǁ__repr____mutmut_orig.__name__ = 'xǁTracebackInfoǁ__repr__'

    def __str__(self):
        return self.get_formatted()

    def xǁTracebackInfoǁget_formatted__mutmut_orig(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_1(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = None
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_2(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'XXTraceback (most recent call last):\nXX'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_3(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'traceback (most recent call last):\n'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_4(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'TRACEBACK (MOST RECENT CALL LAST):\n'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_5(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret = ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_6(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret -= ''.join([f.tb_frame_str() for f in self.frames])
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_7(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret += ''.join(None)
        return ret

    def xǁTracebackInfoǁget_formatted__mutmut_8(self):
        """Returns a string as formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_tb` and
        :func:`traceback.format_stack`.
        """
        ret = 'Traceback (most recent call last):\n'
        ret += 'XXXX'.join([f.tb_frame_str() for f in self.frames])
        return ret
    
    xǁTracebackInfoǁget_formatted__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracebackInfoǁget_formatted__mutmut_1': xǁTracebackInfoǁget_formatted__mutmut_1, 
        'xǁTracebackInfoǁget_formatted__mutmut_2': xǁTracebackInfoǁget_formatted__mutmut_2, 
        'xǁTracebackInfoǁget_formatted__mutmut_3': xǁTracebackInfoǁget_formatted__mutmut_3, 
        'xǁTracebackInfoǁget_formatted__mutmut_4': xǁTracebackInfoǁget_formatted__mutmut_4, 
        'xǁTracebackInfoǁget_formatted__mutmut_5': xǁTracebackInfoǁget_formatted__mutmut_5, 
        'xǁTracebackInfoǁget_formatted__mutmut_6': xǁTracebackInfoǁget_formatted__mutmut_6, 
        'xǁTracebackInfoǁget_formatted__mutmut_7': xǁTracebackInfoǁget_formatted__mutmut_7, 
        'xǁTracebackInfoǁget_formatted__mutmut_8': xǁTracebackInfoǁget_formatted__mutmut_8
    }
    
    def get_formatted(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracebackInfoǁget_formatted__mutmut_orig"), object.__getattribute__(self, "xǁTracebackInfoǁget_formatted__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_formatted.__signature__ = _mutmut_signature(xǁTracebackInfoǁget_formatted__mutmut_orig)
    xǁTracebackInfoǁget_formatted__mutmut_orig.__name__ = 'xǁTracebackInfoǁget_formatted'


class ExceptionInfo:
    """An ExceptionInfo object ties together three main fields suitable
    for representing an instance of an exception: The exception type
    name, a string representation of the exception itself (the
    exception message), and information about the traceback (stored as
    a :class:`TracebackInfo` object).

    These fields line up with :func:`sys.exc_info`, but unlike the
    values returned by that function, ExceptionInfo does not hold any
    references to the real exception or traceback. This property makes
    it suitable for serialization or long-term retention, without
    worrying about formatting pitfalls, circular references, or leaking memory.

    Args:

        exc_type (str): The exception type name.
        exc_msg (str): String representation of the exception value.
        tb_info (TracebackInfo): Information about the stack trace of the
            exception.

    Like the :class:`TracebackInfo`, ExceptionInfo is most commonly
    instantiated from one of its classmethods: :meth:`from_exc_info`
    or :meth:`from_current`.
    """

    #: Override this in inherited types to control the TracebackInfo type used
    tb_info_type = TracebackInfo

    def xǁExceptionInfoǁ__init____mutmut_orig(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = exc_type
        self.exc_msg = exc_msg
        self.tb_info = tb_info

    def xǁExceptionInfoǁ__init____mutmut_1(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = None
        self.exc_msg = exc_msg
        self.tb_info = tb_info

    def xǁExceptionInfoǁ__init____mutmut_2(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = exc_type
        self.exc_msg = None
        self.tb_info = tb_info

    def xǁExceptionInfoǁ__init____mutmut_3(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = exc_type
        self.exc_msg = exc_msg
        self.tb_info = None
    
    xǁExceptionInfoǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁExceptionInfoǁ__init____mutmut_1': xǁExceptionInfoǁ__init____mutmut_1, 
        'xǁExceptionInfoǁ__init____mutmut_2': xǁExceptionInfoǁ__init____mutmut_2, 
        'xǁExceptionInfoǁ__init____mutmut_3': xǁExceptionInfoǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁExceptionInfoǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁExceptionInfoǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁExceptionInfoǁ__init____mutmut_orig)
    xǁExceptionInfoǁ__init____mutmut_orig.__name__ = 'xǁExceptionInfoǁ__init__'

    @classmethod
    def from_exc_info(cls, exc_type, exc_value, traceback):
        """Create an :class:`ExceptionInfo` object from the exception's type,
        value, and traceback, as returned by :func:`sys.exc_info`. See
        also :meth:`from_current`.
        """
        type_str = exc_type.__name__
        type_mod = exc_type.__module__
        if type_mod not in ("__main__", "__builtin__", "exceptions", "builtins"):
            type_str = f'{type_mod}.{type_str}'
        val_str = _some_str(exc_value)
        tb_info = cls.tb_info_type.from_traceback(traceback)
        return cls(type_str, val_str, tb_info)

    @classmethod
    def from_current(cls):
        """Create an :class:`ExceptionInfo` object from the current exception
        being handled, by way of :func:`sys.exc_info`. Will raise an
        exception if no exception is currently being handled.
        """
        return cls.from_exc_info(*sys.exc_info())

    def xǁExceptionInfoǁto_dict__mutmut_orig(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_1(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'XXexc_typeXX': self.exc_type,
                'exc_msg': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_2(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'EXC_TYPE': self.exc_type,
                'exc_msg': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_3(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'XXexc_msgXX': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_4(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'EXC_MSG': self.exc_msg,
                'exc_tb': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_5(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'XXexc_tbXX': self.tb_info.to_dict()}

    def xǁExceptionInfoǁto_dict__mutmut_6(self):
        """Get a :class:`dict` representation of the ExceptionInfo, suitable
        for JSON serialization.
        """
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'EXC_TB': self.tb_info.to_dict()}
    
    xǁExceptionInfoǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁExceptionInfoǁto_dict__mutmut_1': xǁExceptionInfoǁto_dict__mutmut_1, 
        'xǁExceptionInfoǁto_dict__mutmut_2': xǁExceptionInfoǁto_dict__mutmut_2, 
        'xǁExceptionInfoǁto_dict__mutmut_3': xǁExceptionInfoǁto_dict__mutmut_3, 
        'xǁExceptionInfoǁto_dict__mutmut_4': xǁExceptionInfoǁto_dict__mutmut_4, 
        'xǁExceptionInfoǁto_dict__mutmut_5': xǁExceptionInfoǁto_dict__mutmut_5, 
        'xǁExceptionInfoǁto_dict__mutmut_6': xǁExceptionInfoǁto_dict__mutmut_6
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁExceptionInfoǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁExceptionInfoǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁExceptionInfoǁto_dict__mutmut_orig)
    xǁExceptionInfoǁto_dict__mutmut_orig.__name__ = 'xǁExceptionInfoǁto_dict'

    def xǁExceptionInfoǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_1(self):
        cn = None
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        try:
            len_frames = None
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = None
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[+1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-2]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = None
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_7(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 1
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_8(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = None
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_9(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = 'XXXX'
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_10(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = None
        return '<%s [%s: %s] (%s frames%s)>' % args

    def xǁExceptionInfoǁ__repr____mutmut_11(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' / args

    def xǁExceptionInfoǁ__repr____mutmut_12(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return 'XX<%s [%s: %s] (%s frames%s)>XX' % args

    def xǁExceptionInfoǁ__repr____mutmut_13(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = f', last={self.tb_info.frames[-1]!r}'
        except Exception:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%S [%S: %S] (%S FRAMES%S)>' % args
    
    xǁExceptionInfoǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁExceptionInfoǁ__repr____mutmut_1': xǁExceptionInfoǁ__repr____mutmut_1, 
        'xǁExceptionInfoǁ__repr____mutmut_2': xǁExceptionInfoǁ__repr____mutmut_2, 
        'xǁExceptionInfoǁ__repr____mutmut_3': xǁExceptionInfoǁ__repr____mutmut_3, 
        'xǁExceptionInfoǁ__repr____mutmut_4': xǁExceptionInfoǁ__repr____mutmut_4, 
        'xǁExceptionInfoǁ__repr____mutmut_5': xǁExceptionInfoǁ__repr____mutmut_5, 
        'xǁExceptionInfoǁ__repr____mutmut_6': xǁExceptionInfoǁ__repr____mutmut_6, 
        'xǁExceptionInfoǁ__repr____mutmut_7': xǁExceptionInfoǁ__repr____mutmut_7, 
        'xǁExceptionInfoǁ__repr____mutmut_8': xǁExceptionInfoǁ__repr____mutmut_8, 
        'xǁExceptionInfoǁ__repr____mutmut_9': xǁExceptionInfoǁ__repr____mutmut_9, 
        'xǁExceptionInfoǁ__repr____mutmut_10': xǁExceptionInfoǁ__repr____mutmut_10, 
        'xǁExceptionInfoǁ__repr____mutmut_11': xǁExceptionInfoǁ__repr____mutmut_11, 
        'xǁExceptionInfoǁ__repr____mutmut_12': xǁExceptionInfoǁ__repr____mutmut_12, 
        'xǁExceptionInfoǁ__repr____mutmut_13': xǁExceptionInfoǁ__repr____mutmut_13
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁExceptionInfoǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁExceptionInfoǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁExceptionInfoǁ__repr____mutmut_orig)
    xǁExceptionInfoǁ__repr____mutmut_orig.__name__ = 'xǁExceptionInfoǁ__repr__'

    def xǁExceptionInfoǁget_formatted__mutmut_orig(self):
        """Returns a string formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_exception`.
        """
        # TODO: add SyntaxError formatting
        tb_str = self.tb_info.get_formatted()
        return ''.join([tb_str, f'{self.exc_type}: {self.exc_msg}'])

    def xǁExceptionInfoǁget_formatted__mutmut_1(self):
        """Returns a string formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_exception`.
        """
        # TODO: add SyntaxError formatting
        tb_str = None
        return ''.join([tb_str, f'{self.exc_type}: {self.exc_msg}'])

    def xǁExceptionInfoǁget_formatted__mutmut_2(self):
        """Returns a string formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_exception`.
        """
        # TODO: add SyntaxError formatting
        tb_str = self.tb_info.get_formatted()
        return ''.join(None)

    def xǁExceptionInfoǁget_formatted__mutmut_3(self):
        """Returns a string formatted in the traditional Python
        built-in style observable when an exception is not caught. In
        other words, mimics :func:`traceback.format_exception`.
        """
        # TODO: add SyntaxError formatting
        tb_str = self.tb_info.get_formatted()
        return 'XXXX'.join([tb_str, f'{self.exc_type}: {self.exc_msg}'])
    
    xǁExceptionInfoǁget_formatted__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁExceptionInfoǁget_formatted__mutmut_1': xǁExceptionInfoǁget_formatted__mutmut_1, 
        'xǁExceptionInfoǁget_formatted__mutmut_2': xǁExceptionInfoǁget_formatted__mutmut_2, 
        'xǁExceptionInfoǁget_formatted__mutmut_3': xǁExceptionInfoǁget_formatted__mutmut_3
    }
    
    def get_formatted(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁExceptionInfoǁget_formatted__mutmut_orig"), object.__getattribute__(self, "xǁExceptionInfoǁget_formatted__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_formatted.__signature__ = _mutmut_signature(xǁExceptionInfoǁget_formatted__mutmut_orig)
    xǁExceptionInfoǁget_formatted__mutmut_orig.__name__ = 'xǁExceptionInfoǁget_formatted'

    def get_formatted_exception_only(self):
        return f'{self.exc_type}: {self.exc_msg}'


class ContextualCallpoint(Callpoint):
    """The ContextualCallpoint is a :class:`Callpoint` subtype with the
    exact same API and storing two additional values:

      1. :func:`repr` outputs for local variables from the Callpoint's scope
      2. A number of lines before and after the Callpoint's line of code

    The ContextualCallpoint is used by the :class:`ContextualTracebackInfo`.
    """
    def xǁContextualCallpointǁ__init____mutmut_orig(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_1(self, *a, **kw):
        self.local_reprs = None
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_2(self, *a, **kw):
        self.local_reprs = kw.pop(None, {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_3(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', None)
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_4(self, *a, **kw):
        self.local_reprs = kw.pop({})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_5(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', )
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_6(self, *a, **kw):
        self.local_reprs = kw.pop('XXlocal_reprsXX', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_7(self, *a, **kw):
        self.local_reprs = kw.pop('LOCAL_REPRS', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_8(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = None
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_9(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop(None, [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_10(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', None)
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_11(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop([])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_12(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', )
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_13(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('XXpre_linesXX', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_14(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('PRE_LINES', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_15(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = None
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_16(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop(None, [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_17(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', None)
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_18(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop([])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_19(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', )
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_20(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('XXpost_linesXX', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_21(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('POST_LINES', [])
        super().__init__(*a, **kw)
    def xǁContextualCallpointǁ__init____mutmut_22(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(**kw)
    def xǁContextualCallpointǁ__init____mutmut_23(self, *a, **kw):
        self.local_reprs = kw.pop('local_reprs', {})
        self.pre_lines = kw.pop('pre_lines', [])
        self.post_lines = kw.pop('post_lines', [])
        super().__init__(*a, )
    
    xǁContextualCallpointǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextualCallpointǁ__init____mutmut_1': xǁContextualCallpointǁ__init____mutmut_1, 
        'xǁContextualCallpointǁ__init____mutmut_2': xǁContextualCallpointǁ__init____mutmut_2, 
        'xǁContextualCallpointǁ__init____mutmut_3': xǁContextualCallpointǁ__init____mutmut_3, 
        'xǁContextualCallpointǁ__init____mutmut_4': xǁContextualCallpointǁ__init____mutmut_4, 
        'xǁContextualCallpointǁ__init____mutmut_5': xǁContextualCallpointǁ__init____mutmut_5, 
        'xǁContextualCallpointǁ__init____mutmut_6': xǁContextualCallpointǁ__init____mutmut_6, 
        'xǁContextualCallpointǁ__init____mutmut_7': xǁContextualCallpointǁ__init____mutmut_7, 
        'xǁContextualCallpointǁ__init____mutmut_8': xǁContextualCallpointǁ__init____mutmut_8, 
        'xǁContextualCallpointǁ__init____mutmut_9': xǁContextualCallpointǁ__init____mutmut_9, 
        'xǁContextualCallpointǁ__init____mutmut_10': xǁContextualCallpointǁ__init____mutmut_10, 
        'xǁContextualCallpointǁ__init____mutmut_11': xǁContextualCallpointǁ__init____mutmut_11, 
        'xǁContextualCallpointǁ__init____mutmut_12': xǁContextualCallpointǁ__init____mutmut_12, 
        'xǁContextualCallpointǁ__init____mutmut_13': xǁContextualCallpointǁ__init____mutmut_13, 
        'xǁContextualCallpointǁ__init____mutmut_14': xǁContextualCallpointǁ__init____mutmut_14, 
        'xǁContextualCallpointǁ__init____mutmut_15': xǁContextualCallpointǁ__init____mutmut_15, 
        'xǁContextualCallpointǁ__init____mutmut_16': xǁContextualCallpointǁ__init____mutmut_16, 
        'xǁContextualCallpointǁ__init____mutmut_17': xǁContextualCallpointǁ__init____mutmut_17, 
        'xǁContextualCallpointǁ__init____mutmut_18': xǁContextualCallpointǁ__init____mutmut_18, 
        'xǁContextualCallpointǁ__init____mutmut_19': xǁContextualCallpointǁ__init____mutmut_19, 
        'xǁContextualCallpointǁ__init____mutmut_20': xǁContextualCallpointǁ__init____mutmut_20, 
        'xǁContextualCallpointǁ__init____mutmut_21': xǁContextualCallpointǁ__init____mutmut_21, 
        'xǁContextualCallpointǁ__init____mutmut_22': xǁContextualCallpointǁ__init____mutmut_22, 
        'xǁContextualCallpointǁ__init____mutmut_23': xǁContextualCallpointǁ__init____mutmut_23
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextualCallpointǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁContextualCallpointǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁContextualCallpointǁ__init____mutmut_orig)
    xǁContextualCallpointǁ__init____mutmut_orig.__name__ = 'xǁContextualCallpointǁ__init__'

    @classmethod
    def from_frame(cls, frame):
        "Identical to :meth:`Callpoint.from_frame`"
        ret = super().from_frame(frame)
        ret._populate_local_reprs(frame.f_locals)
        ret._populate_context_lines()
        return ret

    @classmethod
    def from_tb(cls, tb):
        "Identical to :meth:`Callpoint.from_tb`"
        ret = super().from_tb(tb)
        ret._populate_local_reprs(tb.tb_frame.f_locals)
        ret._populate_context_lines()
        return ret

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_orig(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_1(self, pivot=9):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_2(self, pivot=8):
        DL, lineno = None
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_3(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = None
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_4(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = ""
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_5(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = None
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_6(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(None, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_7(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, None)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_8(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_9(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, )
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_10(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(1, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_11(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno + pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_12(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = None
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_13(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(None, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_14(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, None, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_15(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, None)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_16(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_17(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_18(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, )
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_19(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(None, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_20(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, None)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_21(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_22(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, )]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_23(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = None
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_24(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = None
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_25(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(None, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_26(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, None, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_27(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, None)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_28(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_29(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_30(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, )
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_31(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(None, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_32(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, None)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_33(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_34(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, )]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_35(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno - 1, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_36(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 2, lineno + 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_37(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 - pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_38(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno - 1 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_39(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 2 + pivot)]
        self.post_lines[:] = post_lines
        return

    def xǁContextualCallpointǁ_populate_context_lines__mutmut_40(self, pivot=8):
        DL, lineno = _DeferredLine, self.lineno
        try:
            module_globals = self.line.module_globals
        except AttributeError:
            module_globals = None
        start_line = max(0, lineno - pivot)
        pre_lines = [DL(self.module_path, ln, module_globals)
                     for ln in range(start_line, lineno)]
        self.pre_lines[:] = pre_lines
        post_lines = [DL(self.module_path, ln, module_globals)
                      for ln in range(lineno + 1, lineno + 1 + pivot)]
        self.post_lines[:] = None
        return
    
    xǁContextualCallpointǁ_populate_context_lines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextualCallpointǁ_populate_context_lines__mutmut_1': xǁContextualCallpointǁ_populate_context_lines__mutmut_1, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_2': xǁContextualCallpointǁ_populate_context_lines__mutmut_2, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_3': xǁContextualCallpointǁ_populate_context_lines__mutmut_3, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_4': xǁContextualCallpointǁ_populate_context_lines__mutmut_4, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_5': xǁContextualCallpointǁ_populate_context_lines__mutmut_5, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_6': xǁContextualCallpointǁ_populate_context_lines__mutmut_6, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_7': xǁContextualCallpointǁ_populate_context_lines__mutmut_7, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_8': xǁContextualCallpointǁ_populate_context_lines__mutmut_8, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_9': xǁContextualCallpointǁ_populate_context_lines__mutmut_9, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_10': xǁContextualCallpointǁ_populate_context_lines__mutmut_10, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_11': xǁContextualCallpointǁ_populate_context_lines__mutmut_11, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_12': xǁContextualCallpointǁ_populate_context_lines__mutmut_12, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_13': xǁContextualCallpointǁ_populate_context_lines__mutmut_13, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_14': xǁContextualCallpointǁ_populate_context_lines__mutmut_14, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_15': xǁContextualCallpointǁ_populate_context_lines__mutmut_15, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_16': xǁContextualCallpointǁ_populate_context_lines__mutmut_16, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_17': xǁContextualCallpointǁ_populate_context_lines__mutmut_17, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_18': xǁContextualCallpointǁ_populate_context_lines__mutmut_18, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_19': xǁContextualCallpointǁ_populate_context_lines__mutmut_19, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_20': xǁContextualCallpointǁ_populate_context_lines__mutmut_20, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_21': xǁContextualCallpointǁ_populate_context_lines__mutmut_21, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_22': xǁContextualCallpointǁ_populate_context_lines__mutmut_22, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_23': xǁContextualCallpointǁ_populate_context_lines__mutmut_23, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_24': xǁContextualCallpointǁ_populate_context_lines__mutmut_24, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_25': xǁContextualCallpointǁ_populate_context_lines__mutmut_25, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_26': xǁContextualCallpointǁ_populate_context_lines__mutmut_26, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_27': xǁContextualCallpointǁ_populate_context_lines__mutmut_27, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_28': xǁContextualCallpointǁ_populate_context_lines__mutmut_28, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_29': xǁContextualCallpointǁ_populate_context_lines__mutmut_29, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_30': xǁContextualCallpointǁ_populate_context_lines__mutmut_30, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_31': xǁContextualCallpointǁ_populate_context_lines__mutmut_31, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_32': xǁContextualCallpointǁ_populate_context_lines__mutmut_32, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_33': xǁContextualCallpointǁ_populate_context_lines__mutmut_33, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_34': xǁContextualCallpointǁ_populate_context_lines__mutmut_34, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_35': xǁContextualCallpointǁ_populate_context_lines__mutmut_35, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_36': xǁContextualCallpointǁ_populate_context_lines__mutmut_36, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_37': xǁContextualCallpointǁ_populate_context_lines__mutmut_37, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_38': xǁContextualCallpointǁ_populate_context_lines__mutmut_38, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_39': xǁContextualCallpointǁ_populate_context_lines__mutmut_39, 
        'xǁContextualCallpointǁ_populate_context_lines__mutmut_40': xǁContextualCallpointǁ_populate_context_lines__mutmut_40
    }
    
    def _populate_context_lines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextualCallpointǁ_populate_context_lines__mutmut_orig"), object.__getattribute__(self, "xǁContextualCallpointǁ_populate_context_lines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _populate_context_lines.__signature__ = _mutmut_signature(xǁContextualCallpointǁ_populate_context_lines__mutmut_orig)
    xǁContextualCallpointǁ_populate_context_lines__mutmut_orig.__name__ = 'xǁContextualCallpointǁ_populate_context_lines'

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_orig(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_1(self, f_locals):
        local_reprs = None
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_2(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = None
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_3(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(None)
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_4(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = None
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_5(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' / type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_6(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = 'XX<unprintable %s object>XX' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_7(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<UNPRINTABLE %S OBJECT>' % type(v).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_8(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' % type(None).__name__
                local_reprs[k] = surrogate
        return

    def xǁContextualCallpointǁ_populate_local_reprs__mutmut_9(self, f_locals):
        local_reprs = self.local_reprs
        for k, v in f_locals.items():
            try:
                local_reprs[k] = repr(v)
            except Exception:
                surrogate = '<unprintable %s object>' % type(v).__name__
                local_reprs[k] = None
        return
    
    xǁContextualCallpointǁ_populate_local_reprs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextualCallpointǁ_populate_local_reprs__mutmut_1': xǁContextualCallpointǁ_populate_local_reprs__mutmut_1, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_2': xǁContextualCallpointǁ_populate_local_reprs__mutmut_2, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_3': xǁContextualCallpointǁ_populate_local_reprs__mutmut_3, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_4': xǁContextualCallpointǁ_populate_local_reprs__mutmut_4, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_5': xǁContextualCallpointǁ_populate_local_reprs__mutmut_5, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_6': xǁContextualCallpointǁ_populate_local_reprs__mutmut_6, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_7': xǁContextualCallpointǁ_populate_local_reprs__mutmut_7, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_8': xǁContextualCallpointǁ_populate_local_reprs__mutmut_8, 
        'xǁContextualCallpointǁ_populate_local_reprs__mutmut_9': xǁContextualCallpointǁ_populate_local_reprs__mutmut_9
    }
    
    def _populate_local_reprs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextualCallpointǁ_populate_local_reprs__mutmut_orig"), object.__getattribute__(self, "xǁContextualCallpointǁ_populate_local_reprs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _populate_local_reprs.__signature__ = _mutmut_signature(xǁContextualCallpointǁ_populate_local_reprs__mutmut_orig)
    xǁContextualCallpointǁ_populate_local_reprs__mutmut_orig.__name__ = 'xǁContextualCallpointǁ_populate_local_reprs'

    def xǁContextualCallpointǁto_dict__mutmut_orig(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_1(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = None
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_2(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = None

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_3(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['XXlocalsXX'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_4(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['LOCALS'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_5(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(None)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_6(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = None
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_7(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno + len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_8(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = None
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_9(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'XXlinenoXX': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_10(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'LINENO': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_11(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line - i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_12(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'XXlineXX': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_13(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'LINE': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_14(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(None)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_15(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(None)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_16(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(None):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_17(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['XXlineXX']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_18(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['LINE']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_19(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                return
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_20(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = None
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_21(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = None

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_22(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['XXpre_linesXX'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_23(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['PRE_LINES'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_24(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = None
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_25(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'XXlinenoXX': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_26(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'LINENO': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_27(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno - i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_28(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'XXlineXX': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_29(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'LINE': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_30(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(None)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_31(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(None)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_32(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = None
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_33(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 1
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_34(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(None):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_35(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['XXlineXX']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_36(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['LINE']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_37(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = None
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_38(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = None
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_39(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last - 1]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_40(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 2]
        ret['post_lines'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_41(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['post_lines'] = None
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_42(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['XXpost_linesXX'] = post_lines
        return ret

    def xǁContextualCallpointǁto_dict__mutmut_43(self):
        """
        Same principle as :meth:`Callpoint.to_dict`, but with the added
        contextual values. With ``ContextualCallpoint.to_dict()``,
        each frame will now be represented like::

          {'func_name': 'print_example',
           'lineno': 0,
           'module_name': 'example_module',
           'module_path': '/home/example/example_module.pyc',
           'lasti': 0,
           'line': 'print "example"',
           'locals': {'variable': '"value"'},
           'pre_lines': ['variable = "value"'],
           'post_lines': []}

        The locals dictionary and line lists are copies and can be mutated
        freely.
        """
        ret = super().to_dict()
        ret['locals'] = dict(self.local_reprs)

        # get the line numbers and textual lines
        # without assuming DeferredLines
        start_line = self.lineno - len(self.pre_lines)
        pre_lines = [{'lineno': start_line + i, 'line': str(l)}
                     for i, l in enumerate(self.pre_lines)]
        # trim off leading empty lines
        for i, item in enumerate(pre_lines):
            if item['line']:
                break
        if i:
            pre_lines = pre_lines[i:]
        ret['pre_lines'] = pre_lines

        # now post_lines
        post_lines = [{'lineno': self.lineno + i, 'line': str(l)}
                      for i, l in enumerate(self.post_lines)]
        _last = 0
        for i, item in enumerate(post_lines):
            if item['line']:
                _last = i
        post_lines = post_lines[:_last + 1]
        ret['POST_LINES'] = post_lines
        return ret
    
    xǁContextualCallpointǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContextualCallpointǁto_dict__mutmut_1': xǁContextualCallpointǁto_dict__mutmut_1, 
        'xǁContextualCallpointǁto_dict__mutmut_2': xǁContextualCallpointǁto_dict__mutmut_2, 
        'xǁContextualCallpointǁto_dict__mutmut_3': xǁContextualCallpointǁto_dict__mutmut_3, 
        'xǁContextualCallpointǁto_dict__mutmut_4': xǁContextualCallpointǁto_dict__mutmut_4, 
        'xǁContextualCallpointǁto_dict__mutmut_5': xǁContextualCallpointǁto_dict__mutmut_5, 
        'xǁContextualCallpointǁto_dict__mutmut_6': xǁContextualCallpointǁto_dict__mutmut_6, 
        'xǁContextualCallpointǁto_dict__mutmut_7': xǁContextualCallpointǁto_dict__mutmut_7, 
        'xǁContextualCallpointǁto_dict__mutmut_8': xǁContextualCallpointǁto_dict__mutmut_8, 
        'xǁContextualCallpointǁto_dict__mutmut_9': xǁContextualCallpointǁto_dict__mutmut_9, 
        'xǁContextualCallpointǁto_dict__mutmut_10': xǁContextualCallpointǁto_dict__mutmut_10, 
        'xǁContextualCallpointǁto_dict__mutmut_11': xǁContextualCallpointǁto_dict__mutmut_11, 
        'xǁContextualCallpointǁto_dict__mutmut_12': xǁContextualCallpointǁto_dict__mutmut_12, 
        'xǁContextualCallpointǁto_dict__mutmut_13': xǁContextualCallpointǁto_dict__mutmut_13, 
        'xǁContextualCallpointǁto_dict__mutmut_14': xǁContextualCallpointǁto_dict__mutmut_14, 
        'xǁContextualCallpointǁto_dict__mutmut_15': xǁContextualCallpointǁto_dict__mutmut_15, 
        'xǁContextualCallpointǁto_dict__mutmut_16': xǁContextualCallpointǁto_dict__mutmut_16, 
        'xǁContextualCallpointǁto_dict__mutmut_17': xǁContextualCallpointǁto_dict__mutmut_17, 
        'xǁContextualCallpointǁto_dict__mutmut_18': xǁContextualCallpointǁto_dict__mutmut_18, 
        'xǁContextualCallpointǁto_dict__mutmut_19': xǁContextualCallpointǁto_dict__mutmut_19, 
        'xǁContextualCallpointǁto_dict__mutmut_20': xǁContextualCallpointǁto_dict__mutmut_20, 
        'xǁContextualCallpointǁto_dict__mutmut_21': xǁContextualCallpointǁto_dict__mutmut_21, 
        'xǁContextualCallpointǁto_dict__mutmut_22': xǁContextualCallpointǁto_dict__mutmut_22, 
        'xǁContextualCallpointǁto_dict__mutmut_23': xǁContextualCallpointǁto_dict__mutmut_23, 
        'xǁContextualCallpointǁto_dict__mutmut_24': xǁContextualCallpointǁto_dict__mutmut_24, 
        'xǁContextualCallpointǁto_dict__mutmut_25': xǁContextualCallpointǁto_dict__mutmut_25, 
        'xǁContextualCallpointǁto_dict__mutmut_26': xǁContextualCallpointǁto_dict__mutmut_26, 
        'xǁContextualCallpointǁto_dict__mutmut_27': xǁContextualCallpointǁto_dict__mutmut_27, 
        'xǁContextualCallpointǁto_dict__mutmut_28': xǁContextualCallpointǁto_dict__mutmut_28, 
        'xǁContextualCallpointǁto_dict__mutmut_29': xǁContextualCallpointǁto_dict__mutmut_29, 
        'xǁContextualCallpointǁto_dict__mutmut_30': xǁContextualCallpointǁto_dict__mutmut_30, 
        'xǁContextualCallpointǁto_dict__mutmut_31': xǁContextualCallpointǁto_dict__mutmut_31, 
        'xǁContextualCallpointǁto_dict__mutmut_32': xǁContextualCallpointǁto_dict__mutmut_32, 
        'xǁContextualCallpointǁto_dict__mutmut_33': xǁContextualCallpointǁto_dict__mutmut_33, 
        'xǁContextualCallpointǁto_dict__mutmut_34': xǁContextualCallpointǁto_dict__mutmut_34, 
        'xǁContextualCallpointǁto_dict__mutmut_35': xǁContextualCallpointǁto_dict__mutmut_35, 
        'xǁContextualCallpointǁto_dict__mutmut_36': xǁContextualCallpointǁto_dict__mutmut_36, 
        'xǁContextualCallpointǁto_dict__mutmut_37': xǁContextualCallpointǁto_dict__mutmut_37, 
        'xǁContextualCallpointǁto_dict__mutmut_38': xǁContextualCallpointǁto_dict__mutmut_38, 
        'xǁContextualCallpointǁto_dict__mutmut_39': xǁContextualCallpointǁto_dict__mutmut_39, 
        'xǁContextualCallpointǁto_dict__mutmut_40': xǁContextualCallpointǁto_dict__mutmut_40, 
        'xǁContextualCallpointǁto_dict__mutmut_41': xǁContextualCallpointǁto_dict__mutmut_41, 
        'xǁContextualCallpointǁto_dict__mutmut_42': xǁContextualCallpointǁto_dict__mutmut_42, 
        'xǁContextualCallpointǁto_dict__mutmut_43': xǁContextualCallpointǁto_dict__mutmut_43
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContextualCallpointǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁContextualCallpointǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁContextualCallpointǁto_dict__mutmut_orig)
    xǁContextualCallpointǁto_dict__mutmut_orig.__name__ = 'xǁContextualCallpointǁto_dict'


class ContextualTracebackInfo(TracebackInfo):
    """The ContextualTracebackInfo type is a :class:`TracebackInfo`
    subtype that is used by :class:`ContextualExceptionInfo` and uses
    the :class:`ContextualCallpoint` as its frame-representing
    primitive.
    """
    callpoint_type = ContextualCallpoint


class ContextualExceptionInfo(ExceptionInfo):
    """The ContextualTracebackInfo type is a :class:`TracebackInfo`
    subtype that uses the :class:`ContextualCallpoint` as its
    frame-representing primitive.

    It carries with it most of the exception information required to
    recreate the widely recognizable "500" page for debugging Django
    applications.
    """
    tb_info_type = ContextualTracebackInfo


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_orig(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_1(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is not None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_2(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(None, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_3(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, None)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_4(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_5(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, )]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_6(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = None
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_7(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = None
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_8(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_9(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("XX__main__XX", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_10(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__MAIN__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_11(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "XXbuiltinsXX", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_12(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "BUILTINS", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_13(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "XXexceptionsXX"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_14(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "EXCEPTIONS"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_15(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = None

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_16(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' - stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_17(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod - '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_18(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + 'XX.XX' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_19(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_20(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(None, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_21(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, None):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_22(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_23(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, ):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_24(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(None, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_25(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, None)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_26(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_27(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, )]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_28(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = None
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_29(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = None
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_30(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename and "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_31(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "XX<string>XX"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_32(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<STRING>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_33(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = None
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_34(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) and '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_35(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(None) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_36(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or 'XX?XX'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_37(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(None)
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_38(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = None
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_39(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = None
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_40(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_41(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append(None)
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_42(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' / badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_43(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('XX    %s\nXX' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_44(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %S\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_45(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_46(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = None
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_47(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].rstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_48(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip(None)[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_49(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.lstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_50(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('XX\nXX')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_51(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = None
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_52(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c and ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_53(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() or c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_54(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or 'XX XX') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_55(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append(None)
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_56(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' / ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_57(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('XX   %s^\nXX' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_58(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %S^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_59(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(None))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_60(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % 'XXXX'.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_61(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = None
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_62(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg and "<no detail available>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_63(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "XX<no detail available>XX"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_64(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<NO DETAIL AVAILABLE>"
    lines.append(f"{stype}: {msg}\n")
    return lines


# TODO: clean up & reimplement -- specifically for syntax errors
def x_format_exception_only__mutmut_65(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append(f'  File "{filename}", line {lineno}\n')
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append(None)
    return lines

x_format_exception_only__mutmut_mutants : ClassVar[MutantDict] = {
'x_format_exception_only__mutmut_1': x_format_exception_only__mutmut_1, 
    'x_format_exception_only__mutmut_2': x_format_exception_only__mutmut_2, 
    'x_format_exception_only__mutmut_3': x_format_exception_only__mutmut_3, 
    'x_format_exception_only__mutmut_4': x_format_exception_only__mutmut_4, 
    'x_format_exception_only__mutmut_5': x_format_exception_only__mutmut_5, 
    'x_format_exception_only__mutmut_6': x_format_exception_only__mutmut_6, 
    'x_format_exception_only__mutmut_7': x_format_exception_only__mutmut_7, 
    'x_format_exception_only__mutmut_8': x_format_exception_only__mutmut_8, 
    'x_format_exception_only__mutmut_9': x_format_exception_only__mutmut_9, 
    'x_format_exception_only__mutmut_10': x_format_exception_only__mutmut_10, 
    'x_format_exception_only__mutmut_11': x_format_exception_only__mutmut_11, 
    'x_format_exception_only__mutmut_12': x_format_exception_only__mutmut_12, 
    'x_format_exception_only__mutmut_13': x_format_exception_only__mutmut_13, 
    'x_format_exception_only__mutmut_14': x_format_exception_only__mutmut_14, 
    'x_format_exception_only__mutmut_15': x_format_exception_only__mutmut_15, 
    'x_format_exception_only__mutmut_16': x_format_exception_only__mutmut_16, 
    'x_format_exception_only__mutmut_17': x_format_exception_only__mutmut_17, 
    'x_format_exception_only__mutmut_18': x_format_exception_only__mutmut_18, 
    'x_format_exception_only__mutmut_19': x_format_exception_only__mutmut_19, 
    'x_format_exception_only__mutmut_20': x_format_exception_only__mutmut_20, 
    'x_format_exception_only__mutmut_21': x_format_exception_only__mutmut_21, 
    'x_format_exception_only__mutmut_22': x_format_exception_only__mutmut_22, 
    'x_format_exception_only__mutmut_23': x_format_exception_only__mutmut_23, 
    'x_format_exception_only__mutmut_24': x_format_exception_only__mutmut_24, 
    'x_format_exception_only__mutmut_25': x_format_exception_only__mutmut_25, 
    'x_format_exception_only__mutmut_26': x_format_exception_only__mutmut_26, 
    'x_format_exception_only__mutmut_27': x_format_exception_only__mutmut_27, 
    'x_format_exception_only__mutmut_28': x_format_exception_only__mutmut_28, 
    'x_format_exception_only__mutmut_29': x_format_exception_only__mutmut_29, 
    'x_format_exception_only__mutmut_30': x_format_exception_only__mutmut_30, 
    'x_format_exception_only__mutmut_31': x_format_exception_only__mutmut_31, 
    'x_format_exception_only__mutmut_32': x_format_exception_only__mutmut_32, 
    'x_format_exception_only__mutmut_33': x_format_exception_only__mutmut_33, 
    'x_format_exception_only__mutmut_34': x_format_exception_only__mutmut_34, 
    'x_format_exception_only__mutmut_35': x_format_exception_only__mutmut_35, 
    'x_format_exception_only__mutmut_36': x_format_exception_only__mutmut_36, 
    'x_format_exception_only__mutmut_37': x_format_exception_only__mutmut_37, 
    'x_format_exception_only__mutmut_38': x_format_exception_only__mutmut_38, 
    'x_format_exception_only__mutmut_39': x_format_exception_only__mutmut_39, 
    'x_format_exception_only__mutmut_40': x_format_exception_only__mutmut_40, 
    'x_format_exception_only__mutmut_41': x_format_exception_only__mutmut_41, 
    'x_format_exception_only__mutmut_42': x_format_exception_only__mutmut_42, 
    'x_format_exception_only__mutmut_43': x_format_exception_only__mutmut_43, 
    'x_format_exception_only__mutmut_44': x_format_exception_only__mutmut_44, 
    'x_format_exception_only__mutmut_45': x_format_exception_only__mutmut_45, 
    'x_format_exception_only__mutmut_46': x_format_exception_only__mutmut_46, 
    'x_format_exception_only__mutmut_47': x_format_exception_only__mutmut_47, 
    'x_format_exception_only__mutmut_48': x_format_exception_only__mutmut_48, 
    'x_format_exception_only__mutmut_49': x_format_exception_only__mutmut_49, 
    'x_format_exception_only__mutmut_50': x_format_exception_only__mutmut_50, 
    'x_format_exception_only__mutmut_51': x_format_exception_only__mutmut_51, 
    'x_format_exception_only__mutmut_52': x_format_exception_only__mutmut_52, 
    'x_format_exception_only__mutmut_53': x_format_exception_only__mutmut_53, 
    'x_format_exception_only__mutmut_54': x_format_exception_only__mutmut_54, 
    'x_format_exception_only__mutmut_55': x_format_exception_only__mutmut_55, 
    'x_format_exception_only__mutmut_56': x_format_exception_only__mutmut_56, 
    'x_format_exception_only__mutmut_57': x_format_exception_only__mutmut_57, 
    'x_format_exception_only__mutmut_58': x_format_exception_only__mutmut_58, 
    'x_format_exception_only__mutmut_59': x_format_exception_only__mutmut_59, 
    'x_format_exception_only__mutmut_60': x_format_exception_only__mutmut_60, 
    'x_format_exception_only__mutmut_61': x_format_exception_only__mutmut_61, 
    'x_format_exception_only__mutmut_62': x_format_exception_only__mutmut_62, 
    'x_format_exception_only__mutmut_63': x_format_exception_only__mutmut_63, 
    'x_format_exception_only__mutmut_64': x_format_exception_only__mutmut_64, 
    'x_format_exception_only__mutmut_65': x_format_exception_only__mutmut_65
}

def format_exception_only(*args, **kwargs):
    result = _mutmut_trampoline(x_format_exception_only__mutmut_orig, x_format_exception_only__mutmut_mutants, args, kwargs)
    return result 

format_exception_only.__signature__ = _mutmut_signature(x_format_exception_only__mutmut_orig)
x_format_exception_only__mutmut_orig.__name__ = 'x_format_exception_only'


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_orig(value):
    try:
        return str(value)
    except Exception:
        pass
    return '<unprintable %s object>' % type(value).__name__


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_1(value):
    try:
        return str(None)
    except Exception:
        pass
    return '<unprintable %s object>' % type(value).__name__


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_2(value):
    try:
        return str(value)
    except Exception:
        pass
    return '<unprintable %s object>' / type(value).__name__


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_3(value):
    try:
        return str(value)
    except Exception:
        pass
    return 'XX<unprintable %s object>XX' % type(value).__name__


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_4(value):
    try:
        return str(value)
    except Exception:
        pass
    return '<UNPRINTABLE %S OBJECT>' % type(value).__name__


# TODO: use asciify, improved if necessary
def x__some_str__mutmut_5(value):
    try:
        return str(value)
    except Exception:
        pass
    return '<unprintable %s object>' % type(None).__name__

x__some_str__mutmut_mutants : ClassVar[MutantDict] = {
'x__some_str__mutmut_1': x__some_str__mutmut_1, 
    'x__some_str__mutmut_2': x__some_str__mutmut_2, 
    'x__some_str__mutmut_3': x__some_str__mutmut_3, 
    'x__some_str__mutmut_4': x__some_str__mutmut_4, 
    'x__some_str__mutmut_5': x__some_str__mutmut_5
}

def _some_str(*args, **kwargs):
    result = _mutmut_trampoline(x__some_str__mutmut_orig, x__some_str__mutmut_mutants, args, kwargs)
    return result 

_some_str.__signature__ = _mutmut_signature(x__some_str__mutmut_orig)
x__some_str__mutmut_orig.__name__ = 'x__some_str'


def x__format_final_exc_line__mutmut_orig(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_1(etype, value):
    valuestr = None
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_2(etype, value):
    valuestr = _some_str(None)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_3(etype, value):
    valuestr = _some_str(value)
    if value is None and not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_4(etype, value):
    valuestr = _some_str(value)
    if value is not None or not valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_5(etype, value):
    valuestr = _some_str(value)
    if value is None or valuestr:
        line = "%s\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_6(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = None
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_7(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" / etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_8(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "XX%s\nXX" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_9(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%S\n" % etype
    else:
        line = f"{etype}: {valuestr}\n"
    return line


def x__format_final_exc_line__mutmut_10(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = None
    return line

x__format_final_exc_line__mutmut_mutants : ClassVar[MutantDict] = {
'x__format_final_exc_line__mutmut_1': x__format_final_exc_line__mutmut_1, 
    'x__format_final_exc_line__mutmut_2': x__format_final_exc_line__mutmut_2, 
    'x__format_final_exc_line__mutmut_3': x__format_final_exc_line__mutmut_3, 
    'x__format_final_exc_line__mutmut_4': x__format_final_exc_line__mutmut_4, 
    'x__format_final_exc_line__mutmut_5': x__format_final_exc_line__mutmut_5, 
    'x__format_final_exc_line__mutmut_6': x__format_final_exc_line__mutmut_6, 
    'x__format_final_exc_line__mutmut_7': x__format_final_exc_line__mutmut_7, 
    'x__format_final_exc_line__mutmut_8': x__format_final_exc_line__mutmut_8, 
    'x__format_final_exc_line__mutmut_9': x__format_final_exc_line__mutmut_9, 
    'x__format_final_exc_line__mutmut_10': x__format_final_exc_line__mutmut_10
}

def _format_final_exc_line(*args, **kwargs):
    result = _mutmut_trampoline(x__format_final_exc_line__mutmut_orig, x__format_final_exc_line__mutmut_mutants, args, kwargs)
    return result 

_format_final_exc_line.__signature__ = _mutmut_signature(x__format_final_exc_line__mutmut_orig)
x__format_final_exc_line__mutmut_orig.__name__ = 'x__format_final_exc_line'


def x_print_exception__mutmut_orig(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_1(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is not None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_2(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = None
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_3(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = None
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_4(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(None, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_5(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, None)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_6(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_7(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, )
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_8(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(None, end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_9(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end=None, file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_10(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=None)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_11(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_12(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_13(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', )

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_14(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(None), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_15(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='XXXX', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_16(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(None, value):
        print(line, end='', file=file)


def x_print_exception__mutmut_17(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, None):
        print(line, end='', file=file)


def x_print_exception__mutmut_18(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(value):
        print(line, end='', file=file)


def x_print_exception__mutmut_19(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, ):
        print(line, end='', file=file)


def x_print_exception__mutmut_20(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(None, end='', file=file)


def x_print_exception__mutmut_21(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end=None, file=file)


def x_print_exception__mutmut_22(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=None)


def x_print_exception__mutmut_23(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(end='', file=file)


def x_print_exception__mutmut_24(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, file=file)


def x_print_exception__mutmut_25(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', )


def x_print_exception__mutmut_26(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='XXXX', file=file)

x_print_exception__mutmut_mutants : ClassVar[MutantDict] = {
'x_print_exception__mutmut_1': x_print_exception__mutmut_1, 
    'x_print_exception__mutmut_2': x_print_exception__mutmut_2, 
    'x_print_exception__mutmut_3': x_print_exception__mutmut_3, 
    'x_print_exception__mutmut_4': x_print_exception__mutmut_4, 
    'x_print_exception__mutmut_5': x_print_exception__mutmut_5, 
    'x_print_exception__mutmut_6': x_print_exception__mutmut_6, 
    'x_print_exception__mutmut_7': x_print_exception__mutmut_7, 
    'x_print_exception__mutmut_8': x_print_exception__mutmut_8, 
    'x_print_exception__mutmut_9': x_print_exception__mutmut_9, 
    'x_print_exception__mutmut_10': x_print_exception__mutmut_10, 
    'x_print_exception__mutmut_11': x_print_exception__mutmut_11, 
    'x_print_exception__mutmut_12': x_print_exception__mutmut_12, 
    'x_print_exception__mutmut_13': x_print_exception__mutmut_13, 
    'x_print_exception__mutmut_14': x_print_exception__mutmut_14, 
    'x_print_exception__mutmut_15': x_print_exception__mutmut_15, 
    'x_print_exception__mutmut_16': x_print_exception__mutmut_16, 
    'x_print_exception__mutmut_17': x_print_exception__mutmut_17, 
    'x_print_exception__mutmut_18': x_print_exception__mutmut_18, 
    'x_print_exception__mutmut_19': x_print_exception__mutmut_19, 
    'x_print_exception__mutmut_20': x_print_exception__mutmut_20, 
    'x_print_exception__mutmut_21': x_print_exception__mutmut_21, 
    'x_print_exception__mutmut_22': x_print_exception__mutmut_22, 
    'x_print_exception__mutmut_23': x_print_exception__mutmut_23, 
    'x_print_exception__mutmut_24': x_print_exception__mutmut_24, 
    'x_print_exception__mutmut_25': x_print_exception__mutmut_25, 
    'x_print_exception__mutmut_26': x_print_exception__mutmut_26
}

def print_exception(*args, **kwargs):
    result = _mutmut_trampoline(x_print_exception__mutmut_orig, x_print_exception__mutmut_mutants, args, kwargs)
    return result 

print_exception.__signature__ = _mutmut_signature(x_print_exception__mutmut_orig)
x_print_exception__mutmut_orig.__name__ = 'x_print_exception'


def x_fix_print_exception__mutmut_orig():
    """
    Sets the default exception hook :func:`sys.excepthook` to the
    :func:`tbutils.print_exception` that uses all the ``tbutils``
    facilities to provide a consistent output behavior.
    """
    sys.excepthook = print_exception


def x_fix_print_exception__mutmut_1():
    """
    Sets the default exception hook :func:`sys.excepthook` to the
    :func:`tbutils.print_exception` that uses all the ``tbutils``
    facilities to provide a consistent output behavior.
    """
    sys.excepthook = None

x_fix_print_exception__mutmut_mutants : ClassVar[MutantDict] = {
'x_fix_print_exception__mutmut_1': x_fix_print_exception__mutmut_1
}

def fix_print_exception(*args, **kwargs):
    result = _mutmut_trampoline(x_fix_print_exception__mutmut_orig, x_fix_print_exception__mutmut_mutants, args, kwargs)
    return result 

fix_print_exception.__signature__ = _mutmut_signature(x_fix_print_exception__mutmut_orig)
x_fix_print_exception__mutmut_orig.__name__ = 'x_fix_print_exception'


_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)'
                       r', in (?P<funcname>.+)$')
_se_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)')
_underline_re = re.compile(r'^[~^ ]*$')

# TODO: ParsedException generator over large bodies of text

class ParsedException:
    """Stores a parsed traceback and exception as would be typically
    output by :func:`sys.excepthook` or
    :func:`traceback.print_exception`.

    .. note:

       Does not currently store SyntaxError details such as column.

    """
    def xǁParsedExceptionǁ__init____mutmut_orig(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(frames or [])
    def xǁParsedExceptionǁ__init____mutmut_1(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = None
        self.exc_msg = exc_msg
        self.frames = list(frames or [])
    def xǁParsedExceptionǁ__init____mutmut_2(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = None
        self.frames = list(frames or [])
    def xǁParsedExceptionǁ__init____mutmut_3(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = None
    def xǁParsedExceptionǁ__init____mutmut_4(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(None)
    def xǁParsedExceptionǁ__init____mutmut_5(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(frames and [])
    
    xǁParsedExceptionǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParsedExceptionǁ__init____mutmut_1': xǁParsedExceptionǁ__init____mutmut_1, 
        'xǁParsedExceptionǁ__init____mutmut_2': xǁParsedExceptionǁ__init____mutmut_2, 
        'xǁParsedExceptionǁ__init____mutmut_3': xǁParsedExceptionǁ__init____mutmut_3, 
        'xǁParsedExceptionǁ__init____mutmut_4': xǁParsedExceptionǁ__init____mutmut_4, 
        'xǁParsedExceptionǁ__init____mutmut_5': xǁParsedExceptionǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParsedExceptionǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁParsedExceptionǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁParsedExceptionǁ__init____mutmut_orig)
    xǁParsedExceptionǁ__init____mutmut_orig.__name__ = 'xǁParsedExceptionǁ__init__'

    @property
    def source_file(self):
        """
        The file path of module containing the function that raised the
        exception, or None if not available.
        """
        try:
            return self.frames[-1]['filepath']
        except IndexError:
            return None

    def xǁParsedExceptionǁto_dict__mutmut_orig(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_1(self):
        "XXGet a copy as a JSON-serializable :class:`dict`.XX"
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_2(self):
        "get a copy as a json-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_3(self):
        "GET A COPY AS A JSON-SERIALIZABLE :CLASS:`DICT`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_4(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'XXexc_typeXX': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_5(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'EXC_TYPE': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_6(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'XXexc_msgXX': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_7(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'EXC_MSG': self.exc_msg,
                'frames': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_8(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'XXframesXX': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_9(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'FRAMES': list(self.frames)}

    def xǁParsedExceptionǁto_dict__mutmut_10(self):
        "Get a copy as a JSON-serializable :class:`dict`."
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': list(None)}
    
    xǁParsedExceptionǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParsedExceptionǁto_dict__mutmut_1': xǁParsedExceptionǁto_dict__mutmut_1, 
        'xǁParsedExceptionǁto_dict__mutmut_2': xǁParsedExceptionǁto_dict__mutmut_2, 
        'xǁParsedExceptionǁto_dict__mutmut_3': xǁParsedExceptionǁto_dict__mutmut_3, 
        'xǁParsedExceptionǁto_dict__mutmut_4': xǁParsedExceptionǁto_dict__mutmut_4, 
        'xǁParsedExceptionǁto_dict__mutmut_5': xǁParsedExceptionǁto_dict__mutmut_5, 
        'xǁParsedExceptionǁto_dict__mutmut_6': xǁParsedExceptionǁto_dict__mutmut_6, 
        'xǁParsedExceptionǁto_dict__mutmut_7': xǁParsedExceptionǁto_dict__mutmut_7, 
        'xǁParsedExceptionǁto_dict__mutmut_8': xǁParsedExceptionǁto_dict__mutmut_8, 
        'xǁParsedExceptionǁto_dict__mutmut_9': xǁParsedExceptionǁto_dict__mutmut_9, 
        'xǁParsedExceptionǁto_dict__mutmut_10': xǁParsedExceptionǁto_dict__mutmut_10
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParsedExceptionǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁParsedExceptionǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁParsedExceptionǁto_dict__mutmut_orig)
    xǁParsedExceptionǁto_dict__mutmut_orig.__name__ = 'xǁParsedExceptionǁto_dict'

    def xǁParsedExceptionǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return ('%s(%r, %r, frames=%r)'
                % (cn, self.exc_type, self.exc_msg, self.frames))

    def xǁParsedExceptionǁ__repr____mutmut_1(self):
        cn = None
        return ('%s(%r, %r, frames=%r)'
                % (cn, self.exc_type, self.exc_msg, self.frames))

    def xǁParsedExceptionǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        return ('%s(%r, %r, frames=%r)' / (cn, self.exc_type, self.exc_msg, self.frames))

    def xǁParsedExceptionǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        return ('XX%s(%r, %r, frames=%r)XX'
                % (cn, self.exc_type, self.exc_msg, self.frames))

    def xǁParsedExceptionǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        return ('%S(%R, %R, FRAMES=%R)'
                % (cn, self.exc_type, self.exc_msg, self.frames))
    
    xǁParsedExceptionǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParsedExceptionǁ__repr____mutmut_1': xǁParsedExceptionǁ__repr____mutmut_1, 
        'xǁParsedExceptionǁ__repr____mutmut_2': xǁParsedExceptionǁ__repr____mutmut_2, 
        'xǁParsedExceptionǁ__repr____mutmut_3': xǁParsedExceptionǁ__repr____mutmut_3, 
        'xǁParsedExceptionǁ__repr____mutmut_4': xǁParsedExceptionǁ__repr____mutmut_4
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParsedExceptionǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁParsedExceptionǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁParsedExceptionǁ__repr____mutmut_orig)
    xǁParsedExceptionǁ__repr____mutmut_orig.__name__ = 'xǁParsedExceptionǁ__repr__'

    def xǁParsedExceptionǁto_string__mutmut_orig(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_1(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = None

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_2(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['XXTraceback (most recent call last):XX']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_3(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_4(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['TRACEBACK (MOST RECENT CALL LAST):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_5(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append(None)
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_6(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(None,
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_7(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           None,
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_8(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           None))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_9(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_10(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_11(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           ))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_12(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('XX  File "{}", line {}, in {}XX'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_13(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  file "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_14(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  FILE "{}", LINE {}, IN {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_15(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['XXfilepathXX'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_16(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['FILEPATH'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_17(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['XXlinenoXX'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_18(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['LINENO'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_19(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['XXfuncnameXX']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_20(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['FUNCNAME']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_21(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = None
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_22(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get(None)
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_23(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('XXsource_lineXX')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_24(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('SOURCE_LINE')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_25(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(None)
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_26(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(None)
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_27(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(None)
        return '\n'.join(lines)

    def xǁParsedExceptionǁto_string__mutmut_28(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return '\n'.join(None)

    def xǁParsedExceptionǁto_string__mutmut_29(self):
        """Formats the exception and its traceback into the standard format,
        as returned by the traceback module.

        ``ParsedException.from_string(text).to_string()`` should yield
        ``text``.

        .. note::

           Note that this method does not output "anchors" (e.g.,
           ``~~~~~^^``), as were added in Python 3.13. See the built-in
           ``traceback`` module if these are necessary.
        """
        lines = ['Traceback (most recent call last):']

        for frame in self.frames:
            lines.append('  File "{}", line {}, in {}'.format(frame['filepath'],
                                                           frame['lineno'],
                                                           frame['funcname']))
            source_line = frame.get('source_line')
            if source_line:
                lines.append(f'    {source_line}')
        if self.exc_msg:
            lines.append(f'{self.exc_type}: {self.exc_msg}')
        else:
            lines.append(f'{self.exc_type}')
        return 'XX\nXX'.join(lines)
    
    xǁParsedExceptionǁto_string__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁParsedExceptionǁto_string__mutmut_1': xǁParsedExceptionǁto_string__mutmut_1, 
        'xǁParsedExceptionǁto_string__mutmut_2': xǁParsedExceptionǁto_string__mutmut_2, 
        'xǁParsedExceptionǁto_string__mutmut_3': xǁParsedExceptionǁto_string__mutmut_3, 
        'xǁParsedExceptionǁto_string__mutmut_4': xǁParsedExceptionǁto_string__mutmut_4, 
        'xǁParsedExceptionǁto_string__mutmut_5': xǁParsedExceptionǁto_string__mutmut_5, 
        'xǁParsedExceptionǁto_string__mutmut_6': xǁParsedExceptionǁto_string__mutmut_6, 
        'xǁParsedExceptionǁto_string__mutmut_7': xǁParsedExceptionǁto_string__mutmut_7, 
        'xǁParsedExceptionǁto_string__mutmut_8': xǁParsedExceptionǁto_string__mutmut_8, 
        'xǁParsedExceptionǁto_string__mutmut_9': xǁParsedExceptionǁto_string__mutmut_9, 
        'xǁParsedExceptionǁto_string__mutmut_10': xǁParsedExceptionǁto_string__mutmut_10, 
        'xǁParsedExceptionǁto_string__mutmut_11': xǁParsedExceptionǁto_string__mutmut_11, 
        'xǁParsedExceptionǁto_string__mutmut_12': xǁParsedExceptionǁto_string__mutmut_12, 
        'xǁParsedExceptionǁto_string__mutmut_13': xǁParsedExceptionǁto_string__mutmut_13, 
        'xǁParsedExceptionǁto_string__mutmut_14': xǁParsedExceptionǁto_string__mutmut_14, 
        'xǁParsedExceptionǁto_string__mutmut_15': xǁParsedExceptionǁto_string__mutmut_15, 
        'xǁParsedExceptionǁto_string__mutmut_16': xǁParsedExceptionǁto_string__mutmut_16, 
        'xǁParsedExceptionǁto_string__mutmut_17': xǁParsedExceptionǁto_string__mutmut_17, 
        'xǁParsedExceptionǁto_string__mutmut_18': xǁParsedExceptionǁto_string__mutmut_18, 
        'xǁParsedExceptionǁto_string__mutmut_19': xǁParsedExceptionǁto_string__mutmut_19, 
        'xǁParsedExceptionǁto_string__mutmut_20': xǁParsedExceptionǁto_string__mutmut_20, 
        'xǁParsedExceptionǁto_string__mutmut_21': xǁParsedExceptionǁto_string__mutmut_21, 
        'xǁParsedExceptionǁto_string__mutmut_22': xǁParsedExceptionǁto_string__mutmut_22, 
        'xǁParsedExceptionǁto_string__mutmut_23': xǁParsedExceptionǁto_string__mutmut_23, 
        'xǁParsedExceptionǁto_string__mutmut_24': xǁParsedExceptionǁto_string__mutmut_24, 
        'xǁParsedExceptionǁto_string__mutmut_25': xǁParsedExceptionǁto_string__mutmut_25, 
        'xǁParsedExceptionǁto_string__mutmut_26': xǁParsedExceptionǁto_string__mutmut_26, 
        'xǁParsedExceptionǁto_string__mutmut_27': xǁParsedExceptionǁto_string__mutmut_27, 
        'xǁParsedExceptionǁto_string__mutmut_28': xǁParsedExceptionǁto_string__mutmut_28, 
        'xǁParsedExceptionǁto_string__mutmut_29': xǁParsedExceptionǁto_string__mutmut_29
    }
    
    def to_string(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁParsedExceptionǁto_string__mutmut_orig"), object.__getattribute__(self, "xǁParsedExceptionǁto_string__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_string.__signature__ = _mutmut_signature(xǁParsedExceptionǁto_string__mutmut_orig)
    xǁParsedExceptionǁto_string__mutmut_orig.__name__ = 'xǁParsedExceptionǁto_string'

    @classmethod
    def from_string(cls, tb_str):
        """Parse a traceback and exception from the text *tb_str*. This text
        is expected to have been decoded, otherwise it will be
        interpreted as UTF-8.

        This method does not search a larger body of text for
        tracebacks. If the first line of the text passed does not
        match one of the known patterns, a :exc:`ValueError` will be
        raised. This method will ignore trailing text after the end of
        the first traceback.

        Args:
            tb_str (str): The traceback text (:class:`unicode` or UTF-8 bytes)
        """
        if not isinstance(tb_str, str):
            tb_str = tb_str.decode('utf-8')
        tb_lines = tb_str.lstrip().splitlines()

        # First off, handle some ignored exceptions. These can be the
        # result of exceptions raised by __del__ during garbage
        # collection
        while tb_lines:
            cl = tb_lines[-1]
            if cl.startswith('Exception ') and cl.endswith('ignored'):
                tb_lines.pop()
            else:
                break
        if tb_lines and tb_lines[0].strip() == 'Traceback (most recent call last):':
            start_line = 1
            frame_re = _frame_re
        elif len(tb_lines) > 1 and tb_lines[-2].lstrip().startswith('^'):
            # This is to handle the slight formatting difference
            # associated with SyntaxErrors, which also don't really
            # have tracebacks
            start_line = 0
            frame_re = _se_frame_re
        else:
            raise ValueError('unrecognized traceback string format')

        frames = []
        line_no = start_line
        while True:
            frame_line = tb_lines[line_no].strip()
            frame_match = frame_re.match(frame_line)
            if frame_match:
                frame_dict = frame_match.groupdict()
                try:
                    next_line = tb_lines[line_no + 1]
                except IndexError:
                    # We read what we could
                    next_line = ''
                next_line_stripped = next_line.strip()
                if (
                        frame_re.match(next_line_stripped) or
                        # The exception message will not be indented
                        # This check is to avoid overrunning on eval-like
                        # tracebacks where the last frame doesn't have source
                        # code in the traceback
                        not next_line.startswith(' ')
                ):
                    frame_dict['source_line'] = ''
                else:
                    frame_dict['source_line'] = next_line_stripped
                    line_no += 1
                if _underline_re.match(tb_lines[line_no + 1]):
                  # To deal with anchors
                  line_no += 1
            else:
                break
            line_no += 1
            frames.append(frame_dict)

        try:
            exc_line = '\n'.join(tb_lines[line_no:])
            exc_type, _, exc_msg = exc_line.partition(': ')
        except Exception:
            exc_type, exc_msg = '', ''

        return cls(exc_type, exc_msg, frames)


ParsedTB = ParsedException  # legacy alias
