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

"""If there is one recurring theme in ``boltons``, it is that Python
has excellent datastructures that constitute a good foundation for
most quick manipulations, as well as building applications. However,
Python usage has grown much faster than builtin data structure
power. Python has a growing need for more advanced general-purpose
data structures which behave intuitively.

The :class:`Table` class is one example. When handed one- or
two-dimensional data, it can provide useful, if basic, text and HTML
renditions of small to medium sized data. It also heuristically
handles recursive data of various formats (lists, dicts, namedtuples,
objects).

For more advanced :class:`Table`-style manipulation check out the
`pandas`_ DataFrame.

.. _pandas: http://pandas.pydata.org/

"""


from html import escape as html_escape
import types
from itertools import islice
from collections.abc import Sequence, Mapping, MutableSequence

_MISSING = object()

"""
Some idle feature thoughts:

* shift around column order without rearranging data
* gotta make it so you can add additional items, not just initialize with
* maybe a shortcut would be to allow adding of Tables to other Tables
* what's the perf of preallocating lists and overwriting items versus
  starting from empty?
* is it possible to effectively tell the difference between when a
  Table is from_data()'d with a single row (list) or with a list of lists?
* CSS: white-space pre-line or pre-wrap maybe?
* Would be nice to support different backends (currently uses lists
  exclusively). Sometimes large datasets come in list-of-dicts and
  list-of-tuples format and it's desirable to cut down processing overhead.

TODO: make iterable on rows?
"""

__all__ = ['Table']
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


def x_to_text__mutmut_orig(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_1(obj, maxlen=None):
    try:
        text = None
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_2(obj, maxlen=None):
    try:
        text = str(None)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_3(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = None
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_4(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(None)
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_5(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(None))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_6(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = None
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_7(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(None)
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_8(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(None))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_9(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen or len(text) > maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_10(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) >= maxlen:
        text = text[:maxlen - 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_11(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = None
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_12(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] - '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_13(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen + 3] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_14(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 4] + '...'
        # TODO: inverse of ljust/rjust/center
    return text


def x_to_text__mutmut_15(obj, maxlen=None):
    try:
        text = str(obj)
    except Exception:
        try:
            text = str(repr(obj))
        except Exception:
            text = str(object.__repr__(obj))
    if maxlen and len(text) > maxlen:
        text = text[:maxlen - 3] + 'XX...XX'
        # TODO: inverse of ljust/rjust/center
    return text

x_to_text__mutmut_mutants : ClassVar[MutantDict] = {
'x_to_text__mutmut_1': x_to_text__mutmut_1, 
    'x_to_text__mutmut_2': x_to_text__mutmut_2, 
    'x_to_text__mutmut_3': x_to_text__mutmut_3, 
    'x_to_text__mutmut_4': x_to_text__mutmut_4, 
    'x_to_text__mutmut_5': x_to_text__mutmut_5, 
    'x_to_text__mutmut_6': x_to_text__mutmut_6, 
    'x_to_text__mutmut_7': x_to_text__mutmut_7, 
    'x_to_text__mutmut_8': x_to_text__mutmut_8, 
    'x_to_text__mutmut_9': x_to_text__mutmut_9, 
    'x_to_text__mutmut_10': x_to_text__mutmut_10, 
    'x_to_text__mutmut_11': x_to_text__mutmut_11, 
    'x_to_text__mutmut_12': x_to_text__mutmut_12, 
    'x_to_text__mutmut_13': x_to_text__mutmut_13, 
    'x_to_text__mutmut_14': x_to_text__mutmut_14, 
    'x_to_text__mutmut_15': x_to_text__mutmut_15
}

def to_text(*args, **kwargs):
    result = _mutmut_trampoline(x_to_text__mutmut_orig, x_to_text__mutmut_mutants, args, kwargs)
    return result 

to_text.__signature__ = _mutmut_signature(x_to_text__mutmut_orig)
x_to_text__mutmut_orig.__name__ = 'x_to_text'


def x_escape_html__mutmut_orig(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(text, quote=True)


def x_escape_html__mutmut_1(obj, maxlen=None):
    text = None
    return html_escape(text, quote=True)


def x_escape_html__mutmut_2(obj, maxlen=None):
    text = to_text(None, maxlen=maxlen)
    return html_escape(text, quote=True)


def x_escape_html__mutmut_3(obj, maxlen=None):
    text = to_text(obj, maxlen=None)
    return html_escape(text, quote=True)


def x_escape_html__mutmut_4(obj, maxlen=None):
    text = to_text(maxlen=maxlen)
    return html_escape(text, quote=True)


def x_escape_html__mutmut_5(obj, maxlen=None):
    text = to_text(obj, )
    return html_escape(text, quote=True)


def x_escape_html__mutmut_6(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(None, quote=True)


def x_escape_html__mutmut_7(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(text, quote=None)


def x_escape_html__mutmut_8(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(quote=True)


def x_escape_html__mutmut_9(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(text, )


def x_escape_html__mutmut_10(obj, maxlen=None):
    text = to_text(obj, maxlen=maxlen)
    return html_escape(text, quote=False)

x_escape_html__mutmut_mutants : ClassVar[MutantDict] = {
'x_escape_html__mutmut_1': x_escape_html__mutmut_1, 
    'x_escape_html__mutmut_2': x_escape_html__mutmut_2, 
    'x_escape_html__mutmut_3': x_escape_html__mutmut_3, 
    'x_escape_html__mutmut_4': x_escape_html__mutmut_4, 
    'x_escape_html__mutmut_5': x_escape_html__mutmut_5, 
    'x_escape_html__mutmut_6': x_escape_html__mutmut_6, 
    'x_escape_html__mutmut_7': x_escape_html__mutmut_7, 
    'x_escape_html__mutmut_8': x_escape_html__mutmut_8, 
    'x_escape_html__mutmut_9': x_escape_html__mutmut_9, 
    'x_escape_html__mutmut_10': x_escape_html__mutmut_10
}

def escape_html(*args, **kwargs):
    result = _mutmut_trampoline(x_escape_html__mutmut_orig, x_escape_html__mutmut_mutants, args, kwargs)
    return result 

escape_html.__signature__ = _mutmut_signature(x_escape_html__mutmut_orig)
x_escape_html__mutmut_orig.__name__ = 'x_escape_html'


_DNR = {type(None), bool, complex, float, type(NotImplemented), slice,
        str, bytes, int,
        types.FunctionType, types.MethodType,
        types.BuiltinFunctionType, types.GeneratorType}


class UnsupportedData(TypeError):
    pass


class InputType:
    def __init__(self, *a, **kw):
        pass

    def xǁInputTypeǁget_entry_seq__mutmut_orig(self, data_seq, headers):
        return [self.get_entry(entry, headers) for entry in data_seq]

    def xǁInputTypeǁget_entry_seq__mutmut_1(self, data_seq, headers):
        return [self.get_entry(None, headers) for entry in data_seq]

    def xǁInputTypeǁget_entry_seq__mutmut_2(self, data_seq, headers):
        return [self.get_entry(entry, None) for entry in data_seq]

    def xǁInputTypeǁget_entry_seq__mutmut_3(self, data_seq, headers):
        return [self.get_entry(headers) for entry in data_seq]

    def xǁInputTypeǁget_entry_seq__mutmut_4(self, data_seq, headers):
        return [self.get_entry(entry, ) for entry in data_seq]
    
    xǁInputTypeǁget_entry_seq__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInputTypeǁget_entry_seq__mutmut_1': xǁInputTypeǁget_entry_seq__mutmut_1, 
        'xǁInputTypeǁget_entry_seq__mutmut_2': xǁInputTypeǁget_entry_seq__mutmut_2, 
        'xǁInputTypeǁget_entry_seq__mutmut_3': xǁInputTypeǁget_entry_seq__mutmut_3, 
        'xǁInputTypeǁget_entry_seq__mutmut_4': xǁInputTypeǁget_entry_seq__mutmut_4
    }
    
    def get_entry_seq(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInputTypeǁget_entry_seq__mutmut_orig"), object.__getattribute__(self, "xǁInputTypeǁget_entry_seq__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry_seq.__signature__ = _mutmut_signature(xǁInputTypeǁget_entry_seq__mutmut_orig)
    xǁInputTypeǁget_entry_seq__mutmut_orig.__name__ = 'xǁInputTypeǁget_entry_seq'


class DictInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, Mapping)

    def xǁDictInputTypeǁguess_headers__mutmut_orig(self, obj):
        return sorted(obj.keys())

    def xǁDictInputTypeǁguess_headers__mutmut_1(self, obj):
        return sorted(None)
    
    xǁDictInputTypeǁguess_headers__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDictInputTypeǁguess_headers__mutmut_1': xǁDictInputTypeǁguess_headers__mutmut_1
    }
    
    def guess_headers(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDictInputTypeǁguess_headers__mutmut_orig"), object.__getattribute__(self, "xǁDictInputTypeǁguess_headers__mutmut_mutants"), args, kwargs, self)
        return result 
    
    guess_headers.__signature__ = _mutmut_signature(xǁDictInputTypeǁguess_headers__mutmut_orig)
    xǁDictInputTypeǁguess_headers__mutmut_orig.__name__ = 'xǁDictInputTypeǁguess_headers'

    def xǁDictInputTypeǁget_entry__mutmut_orig(self, obj, headers):
        return [obj.get(h) for h in headers]

    def xǁDictInputTypeǁget_entry__mutmut_1(self, obj, headers):
        return [obj.get(None) for h in headers]
    
    xǁDictInputTypeǁget_entry__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDictInputTypeǁget_entry__mutmut_1': xǁDictInputTypeǁget_entry__mutmut_1
    }
    
    def get_entry(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDictInputTypeǁget_entry__mutmut_orig"), object.__getattribute__(self, "xǁDictInputTypeǁget_entry__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry.__signature__ = _mutmut_signature(xǁDictInputTypeǁget_entry__mutmut_orig)
    xǁDictInputTypeǁget_entry__mutmut_orig.__name__ = 'xǁDictInputTypeǁget_entry'

    def xǁDictInputTypeǁget_entry_seq__mutmut_orig(self, obj, headers):
        return [[ci.get(h) for h in headers] for ci in obj]

    def xǁDictInputTypeǁget_entry_seq__mutmut_1(self, obj, headers):
        return [[ci.get(None) for h in headers] for ci in obj]
    
    xǁDictInputTypeǁget_entry_seq__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDictInputTypeǁget_entry_seq__mutmut_1': xǁDictInputTypeǁget_entry_seq__mutmut_1
    }
    
    def get_entry_seq(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDictInputTypeǁget_entry_seq__mutmut_orig"), object.__getattribute__(self, "xǁDictInputTypeǁget_entry_seq__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry_seq.__signature__ = _mutmut_signature(xǁDictInputTypeǁget_entry_seq__mutmut_orig)
    xǁDictInputTypeǁget_entry_seq__mutmut_orig.__name__ = 'xǁDictInputTypeǁget_entry_seq'


class ObjectInputType(InputType):
    def xǁObjectInputTypeǁcheck_type__mutmut_orig(self, obj):
        return type(obj) not in _DNR and hasattr(obj, '__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_1(self, obj):
        return type(obj) not in _DNR or hasattr(obj, '__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_2(self, obj):
        return type(None) not in _DNR and hasattr(obj, '__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_3(self, obj):
        return type(obj) in _DNR and hasattr(obj, '__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_4(self, obj):
        return type(obj) not in _DNR and hasattr(None, '__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_5(self, obj):
        return type(obj) not in _DNR and hasattr(obj, None)
    def xǁObjectInputTypeǁcheck_type__mutmut_6(self, obj):
        return type(obj) not in _DNR and hasattr('__class__')
    def xǁObjectInputTypeǁcheck_type__mutmut_7(self, obj):
        return type(obj) not in _DNR and hasattr(obj, )
    def xǁObjectInputTypeǁcheck_type__mutmut_8(self, obj):
        return type(obj) not in _DNR and hasattr(obj, 'XX__class__XX')
    def xǁObjectInputTypeǁcheck_type__mutmut_9(self, obj):
        return type(obj) not in _DNR and hasattr(obj, '__CLASS__')
    
    xǁObjectInputTypeǁcheck_type__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁObjectInputTypeǁcheck_type__mutmut_1': xǁObjectInputTypeǁcheck_type__mutmut_1, 
        'xǁObjectInputTypeǁcheck_type__mutmut_2': xǁObjectInputTypeǁcheck_type__mutmut_2, 
        'xǁObjectInputTypeǁcheck_type__mutmut_3': xǁObjectInputTypeǁcheck_type__mutmut_3, 
        'xǁObjectInputTypeǁcheck_type__mutmut_4': xǁObjectInputTypeǁcheck_type__mutmut_4, 
        'xǁObjectInputTypeǁcheck_type__mutmut_5': xǁObjectInputTypeǁcheck_type__mutmut_5, 
        'xǁObjectInputTypeǁcheck_type__mutmut_6': xǁObjectInputTypeǁcheck_type__mutmut_6, 
        'xǁObjectInputTypeǁcheck_type__mutmut_7': xǁObjectInputTypeǁcheck_type__mutmut_7, 
        'xǁObjectInputTypeǁcheck_type__mutmut_8': xǁObjectInputTypeǁcheck_type__mutmut_8, 
        'xǁObjectInputTypeǁcheck_type__mutmut_9': xǁObjectInputTypeǁcheck_type__mutmut_9
    }
    
    def check_type(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁObjectInputTypeǁcheck_type__mutmut_orig"), object.__getattribute__(self, "xǁObjectInputTypeǁcheck_type__mutmut_mutants"), args, kwargs, self)
        return result 
    
    check_type.__signature__ = _mutmut_signature(xǁObjectInputTypeǁcheck_type__mutmut_orig)
    xǁObjectInputTypeǁcheck_type__mutmut_orig.__name__ = 'xǁObjectInputTypeǁcheck_type'

    def xǁObjectInputTypeǁguess_headers__mutmut_orig(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_1(self, obj):
        headers = None
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_2(self, obj):
        headers = []
        for attr in dir(None):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_3(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = None
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_4(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(None, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_5(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, None)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_6(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_7(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, )
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_8(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                break
            if callable(val):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_9(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(None):
                continue
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_10(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                break
            headers.append(attr)
        return headers

    def xǁObjectInputTypeǁguess_headers__mutmut_11(self, obj):
        headers = []
        for attr in dir(obj):
            # an object's __dict__ could technically have non-string keys
            try:
                val = getattr(obj, attr)
            except Exception:
                # seen on greenlet: `run` shows in dir() but raises
                # AttributeError. Also properties misbehave.
                continue
            if callable(val):
                continue
            headers.append(None)
        return headers
    
    xǁObjectInputTypeǁguess_headers__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁObjectInputTypeǁguess_headers__mutmut_1': xǁObjectInputTypeǁguess_headers__mutmut_1, 
        'xǁObjectInputTypeǁguess_headers__mutmut_2': xǁObjectInputTypeǁguess_headers__mutmut_2, 
        'xǁObjectInputTypeǁguess_headers__mutmut_3': xǁObjectInputTypeǁguess_headers__mutmut_3, 
        'xǁObjectInputTypeǁguess_headers__mutmut_4': xǁObjectInputTypeǁguess_headers__mutmut_4, 
        'xǁObjectInputTypeǁguess_headers__mutmut_5': xǁObjectInputTypeǁguess_headers__mutmut_5, 
        'xǁObjectInputTypeǁguess_headers__mutmut_6': xǁObjectInputTypeǁguess_headers__mutmut_6, 
        'xǁObjectInputTypeǁguess_headers__mutmut_7': xǁObjectInputTypeǁguess_headers__mutmut_7, 
        'xǁObjectInputTypeǁguess_headers__mutmut_8': xǁObjectInputTypeǁguess_headers__mutmut_8, 
        'xǁObjectInputTypeǁguess_headers__mutmut_9': xǁObjectInputTypeǁguess_headers__mutmut_9, 
        'xǁObjectInputTypeǁguess_headers__mutmut_10': xǁObjectInputTypeǁguess_headers__mutmut_10, 
        'xǁObjectInputTypeǁguess_headers__mutmut_11': xǁObjectInputTypeǁguess_headers__mutmut_11
    }
    
    def guess_headers(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁObjectInputTypeǁguess_headers__mutmut_orig"), object.__getattribute__(self, "xǁObjectInputTypeǁguess_headers__mutmut_mutants"), args, kwargs, self)
        return result 
    
    guess_headers.__signature__ = _mutmut_signature(xǁObjectInputTypeǁguess_headers__mutmut_orig)
    xǁObjectInputTypeǁguess_headers__mutmut_orig.__name__ = 'xǁObjectInputTypeǁguess_headers'

    def xǁObjectInputTypeǁget_entry__mutmut_orig(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(obj, h))
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_1(self, obj, headers):
        values = None
        for h in headers:
            try:
                values.append(getattr(obj, h))
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_2(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(None)
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_3(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(None, h))
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_4(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(obj, None))
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_5(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(h))
            except Exception:
                values.append(None)
        return values

    def xǁObjectInputTypeǁget_entry__mutmut_6(self, obj, headers):
        values = []
        for h in headers:
            try:
                values.append(getattr(obj, ))
            except Exception:
                values.append(None)
        return values
    
    xǁObjectInputTypeǁget_entry__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁObjectInputTypeǁget_entry__mutmut_1': xǁObjectInputTypeǁget_entry__mutmut_1, 
        'xǁObjectInputTypeǁget_entry__mutmut_2': xǁObjectInputTypeǁget_entry__mutmut_2, 
        'xǁObjectInputTypeǁget_entry__mutmut_3': xǁObjectInputTypeǁget_entry__mutmut_3, 
        'xǁObjectInputTypeǁget_entry__mutmut_4': xǁObjectInputTypeǁget_entry__mutmut_4, 
        'xǁObjectInputTypeǁget_entry__mutmut_5': xǁObjectInputTypeǁget_entry__mutmut_5, 
        'xǁObjectInputTypeǁget_entry__mutmut_6': xǁObjectInputTypeǁget_entry__mutmut_6
    }
    
    def get_entry(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁObjectInputTypeǁget_entry__mutmut_orig"), object.__getattribute__(self, "xǁObjectInputTypeǁget_entry__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry.__signature__ = _mutmut_signature(xǁObjectInputTypeǁget_entry__mutmut_orig)
    xǁObjectInputTypeǁget_entry__mutmut_orig.__name__ = 'xǁObjectInputTypeǁget_entry'


# might be better to hardcode list support since it's so close to the
# core or might be better to make this the copy-style from_* importer
# and have the non-copy style be hardcoded in __init__
class ListInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, MutableSequence)

    def guess_headers(self, obj):
        return None

    def get_entry(self, obj, headers):
        return obj

    def get_entry_seq(self, obj_seq, headers):
        return obj_seq


class TupleInputType(InputType):
    def check_type(self, obj):
        return isinstance(obj, tuple)

    def guess_headers(self, obj):
        return None

    def xǁTupleInputTypeǁget_entry__mutmut_orig(self, obj, headers):
        return list(obj)

    def xǁTupleInputTypeǁget_entry__mutmut_1(self, obj, headers):
        return list(None)
    
    xǁTupleInputTypeǁget_entry__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTupleInputTypeǁget_entry__mutmut_1': xǁTupleInputTypeǁget_entry__mutmut_1
    }
    
    def get_entry(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTupleInputTypeǁget_entry__mutmut_orig"), object.__getattribute__(self, "xǁTupleInputTypeǁget_entry__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry.__signature__ = _mutmut_signature(xǁTupleInputTypeǁget_entry__mutmut_orig)
    xǁTupleInputTypeǁget_entry__mutmut_orig.__name__ = 'xǁTupleInputTypeǁget_entry'

    def xǁTupleInputTypeǁget_entry_seq__mutmut_orig(self, obj_seq, headers):
        return [list(t) for t in obj_seq]

    def xǁTupleInputTypeǁget_entry_seq__mutmut_1(self, obj_seq, headers):
        return [list(None) for t in obj_seq]
    
    xǁTupleInputTypeǁget_entry_seq__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTupleInputTypeǁget_entry_seq__mutmut_1': xǁTupleInputTypeǁget_entry_seq__mutmut_1
    }
    
    def get_entry_seq(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTupleInputTypeǁget_entry_seq__mutmut_orig"), object.__getattribute__(self, "xǁTupleInputTypeǁget_entry_seq__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry_seq.__signature__ = _mutmut_signature(xǁTupleInputTypeǁget_entry_seq__mutmut_orig)
    xǁTupleInputTypeǁget_entry_seq__mutmut_orig.__name__ = 'xǁTupleInputTypeǁget_entry_seq'


class NamedTupleInputType(InputType):
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_orig(self, obj):
        return hasattr(obj, '_fields') and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_1(self, obj):
        return hasattr(obj, '_fields') or isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_2(self, obj):
        return hasattr(None, '_fields') and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_3(self, obj):
        return hasattr(obj, None) and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_4(self, obj):
        return hasattr('_fields') and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_5(self, obj):
        return hasattr(obj, ) and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_6(self, obj):
        return hasattr(obj, 'XX_fieldsXX') and isinstance(obj, tuple)
    def xǁNamedTupleInputTypeǁcheck_type__mutmut_7(self, obj):
        return hasattr(obj, '_FIELDS') and isinstance(obj, tuple)
    
    xǁNamedTupleInputTypeǁcheck_type__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNamedTupleInputTypeǁcheck_type__mutmut_1': xǁNamedTupleInputTypeǁcheck_type__mutmut_1, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_2': xǁNamedTupleInputTypeǁcheck_type__mutmut_2, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_3': xǁNamedTupleInputTypeǁcheck_type__mutmut_3, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_4': xǁNamedTupleInputTypeǁcheck_type__mutmut_4, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_5': xǁNamedTupleInputTypeǁcheck_type__mutmut_5, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_6': xǁNamedTupleInputTypeǁcheck_type__mutmut_6, 
        'xǁNamedTupleInputTypeǁcheck_type__mutmut_7': xǁNamedTupleInputTypeǁcheck_type__mutmut_7
    }
    
    def check_type(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNamedTupleInputTypeǁcheck_type__mutmut_orig"), object.__getattribute__(self, "xǁNamedTupleInputTypeǁcheck_type__mutmut_mutants"), args, kwargs, self)
        return result 
    
    check_type.__signature__ = _mutmut_signature(xǁNamedTupleInputTypeǁcheck_type__mutmut_orig)
    xǁNamedTupleInputTypeǁcheck_type__mutmut_orig.__name__ = 'xǁNamedTupleInputTypeǁcheck_type'

    def xǁNamedTupleInputTypeǁguess_headers__mutmut_orig(self, obj):
        return list(obj._fields)

    def xǁNamedTupleInputTypeǁguess_headers__mutmut_1(self, obj):
        return list(None)
    
    xǁNamedTupleInputTypeǁguess_headers__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNamedTupleInputTypeǁguess_headers__mutmut_1': xǁNamedTupleInputTypeǁguess_headers__mutmut_1
    }
    
    def guess_headers(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNamedTupleInputTypeǁguess_headers__mutmut_orig"), object.__getattribute__(self, "xǁNamedTupleInputTypeǁguess_headers__mutmut_mutants"), args, kwargs, self)
        return result 
    
    guess_headers.__signature__ = _mutmut_signature(xǁNamedTupleInputTypeǁguess_headers__mutmut_orig)
    xǁNamedTupleInputTypeǁguess_headers__mutmut_orig.__name__ = 'xǁNamedTupleInputTypeǁguess_headers'

    def xǁNamedTupleInputTypeǁget_entry__mutmut_orig(self, obj, headers):
        return [getattr(obj, h, None) for h in headers]

    def xǁNamedTupleInputTypeǁget_entry__mutmut_1(self, obj, headers):
        return [getattr(None, h, None) for h in headers]

    def xǁNamedTupleInputTypeǁget_entry__mutmut_2(self, obj, headers):
        return [getattr(obj, None, None) for h in headers]

    def xǁNamedTupleInputTypeǁget_entry__mutmut_3(self, obj, headers):
        return [getattr(h, None) for h in headers]

    def xǁNamedTupleInputTypeǁget_entry__mutmut_4(self, obj, headers):
        return [getattr(obj, None) for h in headers]

    def xǁNamedTupleInputTypeǁget_entry__mutmut_5(self, obj, headers):
        return [getattr(obj, h, ) for h in headers]
    
    xǁNamedTupleInputTypeǁget_entry__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNamedTupleInputTypeǁget_entry__mutmut_1': xǁNamedTupleInputTypeǁget_entry__mutmut_1, 
        'xǁNamedTupleInputTypeǁget_entry__mutmut_2': xǁNamedTupleInputTypeǁget_entry__mutmut_2, 
        'xǁNamedTupleInputTypeǁget_entry__mutmut_3': xǁNamedTupleInputTypeǁget_entry__mutmut_3, 
        'xǁNamedTupleInputTypeǁget_entry__mutmut_4': xǁNamedTupleInputTypeǁget_entry__mutmut_4, 
        'xǁNamedTupleInputTypeǁget_entry__mutmut_5': xǁNamedTupleInputTypeǁget_entry__mutmut_5
    }
    
    def get_entry(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNamedTupleInputTypeǁget_entry__mutmut_orig"), object.__getattribute__(self, "xǁNamedTupleInputTypeǁget_entry__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry.__signature__ = _mutmut_signature(xǁNamedTupleInputTypeǁget_entry__mutmut_orig)
    xǁNamedTupleInputTypeǁget_entry__mutmut_orig.__name__ = 'xǁNamedTupleInputTypeǁget_entry'

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_orig(self, obj_seq, headers):
        return [[getattr(obj, h, None) for h in headers] for obj in obj_seq]

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_1(self, obj_seq, headers):
        return [[getattr(None, h, None) for h in headers] for obj in obj_seq]

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_2(self, obj_seq, headers):
        return [[getattr(obj, None, None) for h in headers] for obj in obj_seq]

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_3(self, obj_seq, headers):
        return [[getattr(h, None) for h in headers] for obj in obj_seq]

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_4(self, obj_seq, headers):
        return [[getattr(obj, None) for h in headers] for obj in obj_seq]

    def xǁNamedTupleInputTypeǁget_entry_seq__mutmut_5(self, obj_seq, headers):
        return [[getattr(obj, h, ) for h in headers] for obj in obj_seq]
    
    xǁNamedTupleInputTypeǁget_entry_seq__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNamedTupleInputTypeǁget_entry_seq__mutmut_1': xǁNamedTupleInputTypeǁget_entry_seq__mutmut_1, 
        'xǁNamedTupleInputTypeǁget_entry_seq__mutmut_2': xǁNamedTupleInputTypeǁget_entry_seq__mutmut_2, 
        'xǁNamedTupleInputTypeǁget_entry_seq__mutmut_3': xǁNamedTupleInputTypeǁget_entry_seq__mutmut_3, 
        'xǁNamedTupleInputTypeǁget_entry_seq__mutmut_4': xǁNamedTupleInputTypeǁget_entry_seq__mutmut_4, 
        'xǁNamedTupleInputTypeǁget_entry_seq__mutmut_5': xǁNamedTupleInputTypeǁget_entry_seq__mutmut_5
    }
    
    def get_entry_seq(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNamedTupleInputTypeǁget_entry_seq__mutmut_orig"), object.__getattribute__(self, "xǁNamedTupleInputTypeǁget_entry_seq__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entry_seq.__signature__ = _mutmut_signature(xǁNamedTupleInputTypeǁget_entry_seq__mutmut_orig)
    xǁNamedTupleInputTypeǁget_entry_seq__mutmut_orig.__name__ = 'xǁNamedTupleInputTypeǁget_entry_seq'


class Table:
    """
    This Table class is meant to be simple, low-overhead, and extensible. Its
    most common use would be for translation between in-memory data
    structures and serialization formats, such as HTML and console-ready text.

    As such, it stores data in list-of-lists format, and *does not* copy
    lists passed in. It also reserves the right to modify those lists in a
    "filling" process, whereby short lists are extended to the width of
    the table (usually determined by number of headers). This greatly
    reduces overhead and processing/validation that would have to occur
    otherwise.

    General description of headers behavior:

    Headers describe the columns, but are not part of the data, however,
    if the *headers* argument is omitted, Table tries to infer header
    names from the data. It is possible to have a table with no headers,
    just pass in ``headers=None``.

    Supported inputs:

    * :class:`list` of :class:`list` objects
    * :class:`dict` (list/single)
    * :class:`object` (list/single)
    * :class:`collections.namedtuple` (list/single)
    * TODO: DB API cursor?
    * TODO: json

    Supported outputs:

    * HTML
    * Pretty text (also usable as GF Markdown)
    * TODO: CSV
    * TODO: json
    * TODO: json lines

    To minimize resident size, the Table data is stored as a list of lists.
    """

    # order definitely matters here
    _input_types = [DictInputType(), ListInputType(),
                    NamedTupleInputType(), TupleInputType(),
                    ObjectInputType()]

    _html_tr, _html_tr_close = '<tr>', '</tr>'
    _html_th, _html_th_close = '<th>', '</th>'
    _html_td, _html_td_close = '<td>', '</td>'
    _html_thead, _html_thead_close = '<thead>', '</thead>'
    _html_tbody, _html_tbody_close = '<tbody>', '</tbody>'

    # _html_tfoot, _html_tfoot_close = '<tfoot>', '</tfoot>'
    _html_table_tag, _html_table_tag_close = '<table>', '</table>'

    def xǁTableǁ__init____mutmut_orig(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_1(self, data=None, headers=_MISSING, metadata=None):
        if headers is not _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_2(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = None
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_3(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = None
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_4(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(None), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_5(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[1]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_6(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(None, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_7(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, None, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_8(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_9(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_10(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, )
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_11(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 2, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_12(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = None
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_13(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers and []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_14(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = None
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_15(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata and {}
        self._data = []
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_16(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = None
        self._width = 0

        self.extend(data)

    def xǁTableǁ__init____mutmut_17(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = None

        self.extend(data)

    def xǁTableǁ__init____mutmut_18(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 1

        self.extend(data)

    def xǁTableǁ__init____mutmut_19(self, data=None, headers=_MISSING, metadata=None):
        if headers is _MISSING:
            headers = []
            if data:
                headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self.metadata = metadata or {}
        self._data = []
        self._width = 0

        self.extend(None)
    
    xǁTableǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ__init____mutmut_1': xǁTableǁ__init____mutmut_1, 
        'xǁTableǁ__init____mutmut_2': xǁTableǁ__init____mutmut_2, 
        'xǁTableǁ__init____mutmut_3': xǁTableǁ__init____mutmut_3, 
        'xǁTableǁ__init____mutmut_4': xǁTableǁ__init____mutmut_4, 
        'xǁTableǁ__init____mutmut_5': xǁTableǁ__init____mutmut_5, 
        'xǁTableǁ__init____mutmut_6': xǁTableǁ__init____mutmut_6, 
        'xǁTableǁ__init____mutmut_7': xǁTableǁ__init____mutmut_7, 
        'xǁTableǁ__init____mutmut_8': xǁTableǁ__init____mutmut_8, 
        'xǁTableǁ__init____mutmut_9': xǁTableǁ__init____mutmut_9, 
        'xǁTableǁ__init____mutmut_10': xǁTableǁ__init____mutmut_10, 
        'xǁTableǁ__init____mutmut_11': xǁTableǁ__init____mutmut_11, 
        'xǁTableǁ__init____mutmut_12': xǁTableǁ__init____mutmut_12, 
        'xǁTableǁ__init____mutmut_13': xǁTableǁ__init____mutmut_13, 
        'xǁTableǁ__init____mutmut_14': xǁTableǁ__init____mutmut_14, 
        'xǁTableǁ__init____mutmut_15': xǁTableǁ__init____mutmut_15, 
        'xǁTableǁ__init____mutmut_16': xǁTableǁ__init____mutmut_16, 
        'xǁTableǁ__init____mutmut_17': xǁTableǁ__init____mutmut_17, 
        'xǁTableǁ__init____mutmut_18': xǁTableǁ__init____mutmut_18, 
        'xǁTableǁ__init____mutmut_19': xǁTableǁ__init____mutmut_19
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTableǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTableǁ__init____mutmut_orig)
    xǁTableǁ__init____mutmut_orig.__name__ = 'xǁTableǁ__init__'

    def xǁTableǁextend__mutmut_orig(self, data):
        """
        Append the given data to the end of the Table.
        """
        if not data:
            return
        self._data.extend(data)
        self._set_width()
        self._fill()

    def xǁTableǁextend__mutmut_1(self, data):
        """
        Append the given data to the end of the Table.
        """
        if data:
            return
        self._data.extend(data)
        self._set_width()
        self._fill()

    def xǁTableǁextend__mutmut_2(self, data):
        """
        Append the given data to the end of the Table.
        """
        if not data:
            return
        self._data.extend(None)
        self._set_width()
        self._fill()
    
    xǁTableǁextend__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁextend__mutmut_1': xǁTableǁextend__mutmut_1, 
        'xǁTableǁextend__mutmut_2': xǁTableǁextend__mutmut_2
    }
    
    def extend(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁextend__mutmut_orig"), object.__getattribute__(self, "xǁTableǁextend__mutmut_mutants"), args, kwargs, self)
        return result 
    
    extend.__signature__ = _mutmut_signature(xǁTableǁextend__mutmut_orig)
    xǁTableǁextend__mutmut_orig.__name__ = 'xǁTableǁextend'

    def xǁTableǁ_set_width__mutmut_orig(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self._data])

    def xǁTableǁ_set_width__mutmut_1(self, reset=True):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self._data])

    def xǁTableǁ_set_width__mutmut_2(self, reset=False):
        if reset:
            self._width = None
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self._data])

    def xǁTableǁ_set_width__mutmut_3(self, reset=False):
        if reset:
            self._width = 1
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self._data])

    def xǁTableǁ_set_width__mutmut_4(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = None
            return
        self._width = max([len(d) for d in self._data])

    def xǁTableǁ_set_width__mutmut_5(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = None

    def xǁTableǁ_set_width__mutmut_6(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max(None)
    
    xǁTableǁ_set_width__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ_set_width__mutmut_1': xǁTableǁ_set_width__mutmut_1, 
        'xǁTableǁ_set_width__mutmut_2': xǁTableǁ_set_width__mutmut_2, 
        'xǁTableǁ_set_width__mutmut_3': xǁTableǁ_set_width__mutmut_3, 
        'xǁTableǁ_set_width__mutmut_4': xǁTableǁ_set_width__mutmut_4, 
        'xǁTableǁ_set_width__mutmut_5': xǁTableǁ_set_width__mutmut_5, 
        'xǁTableǁ_set_width__mutmut_6': xǁTableǁ_set_width__mutmut_6
    }
    
    def _set_width(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ_set_width__mutmut_orig"), object.__getattribute__(self, "xǁTableǁ_set_width__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_width.__signature__ = _mutmut_signature(xǁTableǁ_set_width__mutmut_orig)
    xǁTableǁ_set_width__mutmut_orig.__name__ = 'xǁTableǁ_set_width'

    def xǁTableǁ_fill__mutmut_orig(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_1(self):
        width, filler = None
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_2(self):
        width, filler = self._width, [None]
        if width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_3(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = None
            if rem > 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_4(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width + len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_5(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem >= 0:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_6(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 1:
                d.extend(filler * rem)
        return

    def xǁTableǁ_fill__mutmut_7(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(None)
        return

    def xǁTableǁ_fill__mutmut_8(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler / rem)
        return
    
    xǁTableǁ_fill__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ_fill__mutmut_1': xǁTableǁ_fill__mutmut_1, 
        'xǁTableǁ_fill__mutmut_2': xǁTableǁ_fill__mutmut_2, 
        'xǁTableǁ_fill__mutmut_3': xǁTableǁ_fill__mutmut_3, 
        'xǁTableǁ_fill__mutmut_4': xǁTableǁ_fill__mutmut_4, 
        'xǁTableǁ_fill__mutmut_5': xǁTableǁ_fill__mutmut_5, 
        'xǁTableǁ_fill__mutmut_6': xǁTableǁ_fill__mutmut_6, 
        'xǁTableǁ_fill__mutmut_7': xǁTableǁ_fill__mutmut_7, 
        'xǁTableǁ_fill__mutmut_8': xǁTableǁ_fill__mutmut_8
    }
    
    def _fill(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ_fill__mutmut_orig"), object.__getattribute__(self, "xǁTableǁ_fill__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _fill.__signature__ = _mutmut_signature(xǁTableǁ_fill__mutmut_orig)
    xǁTableǁ_fill__mutmut_orig.__name__ = 'xǁTableǁ_fill'

    @classmethod
    def from_dict(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from a :class:`dict`. Operates the same as
        :meth:`from_data`, but forces interpretation of the data as a
        Mapping.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=DictInputType(),
                             metadata=metadata)

    @classmethod
    def from_list(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from a :class:`list`. Operates the same as
        :meth:`from_data`, but forces the interpretation of the data
        as a Sequence.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=ListInputType(),
                             metadata=metadata)

    @classmethod
    def from_object(cls, data, headers=_MISSING, max_depth=1, metadata=None):
        """Create a Table from an :class:`object`. Operates the same as
        :meth:`from_data`, but forces the interpretation of the data
        as an object. May be useful for some :class:`dict` and
        :class:`list` subtypes.
        """
        return cls.from_data(data=data, headers=headers,
                             max_depth=max_depth, _data_type=ObjectInputType(),
                             metadata=metadata)

    @classmethod
    def from_data(cls, data, headers=_MISSING, max_depth=1, **kwargs):

        """Create a Table from any supported data, heuristically
        selecting how to represent the data in Table format.

        Args:
            data (object): Any object or iterable with data to be
                imported to the Table.

            headers (iterable): An iterable of headers to be matched
                to the data. If not explicitly passed, headers will be
                guessed for certain datatypes.

            max_depth (int): The level to which nested Tables should
                be created (default: 1).

            _data_type (InputType subclass): For advanced use cases,
                do not guess the type of the input data, use this data
                type instead.
        """
        # TODO: seen/cycle detection/reuse ?
        # maxdepth follows the same behavior as find command
        # i.e., it doesn't work if max_depth=0 is passed in
        metadata = kwargs.pop('metadata', None)
        _data_type = kwargs.pop('_data_type', None)

        if max_depth < 1:
            # return data instead?
            return cls(headers=headers, metadata=metadata)
        is_seq = isinstance(data, Sequence)
        if is_seq:
            if not data:
                return cls(headers=headers, metadata=metadata)
            to_check = data[0]
            if not _data_type:
                for it in cls._input_types:
                    if it.check_type(to_check):
                        _data_type = it
                        break
                else:
                    # not particularly happy about this rewind-y approach
                    is_seq = False
                    to_check = data
        else:
            if type(data) in _DNR:
                # hmm, got scalar data.
                # raise an exception or make an exception, nahmsayn?
                return cls([[data]], headers=headers, metadata=metadata)
            to_check = data
        if not _data_type:
            for it in cls._input_types:
                if it.check_type(to_check):
                    _data_type = it
                    break
            else:
                raise UnsupportedData('unsupported data type %r'
                                      % type(data))
        if headers is _MISSING:
            headers = _data_type.guess_headers(to_check)
        if is_seq:
            entries = _data_type.get_entry_seq(data, headers)
        else:
            entries = [_data_type.get_entry(data, headers)]
        if max_depth > 1:
            new_max_depth = max_depth - 1
            for i, entry in enumerate(entries):
                for j, cell in enumerate(entry):
                    if type(cell) in _DNR:
                        # optimization to avoid function overhead
                        continue
                    try:
                        entries[i][j] = cls.from_data(cell,
                                                      max_depth=new_max_depth)
                    except UnsupportedData:
                        continue
        return cls(entries, headers=headers, metadata=metadata)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

    def xǁTableǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        if self.headers:
            return f'{cn}(headers={self.headers!r}, data={self._data!r})'
        else:
            return f'{cn}({self._data!r})'

    def xǁTableǁ__repr____mutmut_1(self):
        cn = None
        if self.headers:
            return f'{cn}(headers={self.headers!r}, data={self._data!r})'
        else:
            return f'{cn}({self._data!r})'
    
    xǁTableǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ__repr____mutmut_1': xǁTableǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁTableǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁTableǁ__repr____mutmut_orig)
    xǁTableǁ__repr____mutmut_orig.__name__ = 'xǁTableǁ__repr__'

    def xǁTableǁto_html__mutmut_orig(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_1(self, orientation=None, wrapped=False,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_2(self, orientation=None, wrapped=True,
                with_headers=False, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_3(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=False,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_4(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=True, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_5(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=2):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_6(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = None
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_7(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = None
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_8(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata or self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_9(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = None
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_10(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(None,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_11(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=None)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_12(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_13(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             )
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_14(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = None
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_15(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=None,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_16(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=None,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_17(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=None,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_18(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=None)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_19(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_20(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_21(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_22(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   )
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_23(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=False,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_24(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=True,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_25(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata == 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_26(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'XXbottomXX':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_27(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'BOTTOM':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_28(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(None)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_29(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append(None)

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_30(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('XX<br />XX')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_31(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<BR />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_32(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers or self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_33(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(None)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_34(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend(None)
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_35(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] / (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_36(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width + len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_37(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(None)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_38(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = None
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_39(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation and 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_40(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'XXautoXX'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_41(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'AUTO'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_42(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = None
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_43(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].upper()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_44(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[1].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_45(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol != 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_46(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'XXaXX':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_47(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'A':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_48(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = None
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_49(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'XXhXX' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_50(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'H' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_51(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) >= 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_52(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 2 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_53(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'XXvXX'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_54(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'V'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_55(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol != 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_56(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'XXhXX':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_57(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'H':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_58(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(None, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_59(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=None,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_60(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=None)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_61(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_62(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_63(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            )
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_64(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol != 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_65(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'XXvXX':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_66(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'V':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_67(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(None, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_68(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=None,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_69(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=None)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_70(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_71(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_72(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          )
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_73(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError(None)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_74(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" / orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_75(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("XXexpected one of 'auto', 'vertical', orXX"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_76(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("EXPECTED ONE OF 'AUTO', 'VERTICAL', OR"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_77(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             "XX 'horizontal', not %rXX" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_78(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'HORIZONTAL', NOT %R" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_79(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata or with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_80(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata or self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_81(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata != 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_82(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'XXbottomXX':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_83(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'BOTTOM':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_84(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append(None)
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_85(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('XX<br />XX')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_86(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<BR />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_87(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(None)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_88(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(None)
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_89(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = None
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_90(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = 'XX\nXX' if with_newlines else ''
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_91(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else 'XXXX'
        return sep.join(lines)

    def xǁTableǁto_html__mutmut_92(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True,
                with_metadata=False, max_depth=1):
        """Render this Table to HTML. Configure the structure of Table
        HTML by subclassing and overriding ``_html_*`` class
        attributes.

        Args:
            orientation (str): one of 'auto', 'horizontal', or
                'vertical' (or the first letter of any of
                those). Default 'auto'.
            wrapped (bool): whether or not to include the wrapping
                '<table></table>' tags. Default ``True``, set to
                ``False`` if appending multiple Table outputs or an
                otherwise customized HTML wrapping tag is needed.
            with_newlines (bool): Set to ``True`` if output should
                include added newlines to make the HTML more
                readable. Default ``False``.
            with_metadata (bool/str): Set to ``True`` if output should
                be preceded with a Table of preset metadata, if it
                exists. Set to special value ``'bottom'`` if the
                metadata Table HTML should come *after* the main HTML output.
            max_depth (int): Indicate how deeply to nest HTML tables
                before simply reverting to :func:`repr`-ing the nested
                data.

        Returns:
            A text string of the HTML of the rendered table.

        """
        lines = []
        headers = []
        if with_metadata and self.metadata:
            metadata_table = Table.from_data(self.metadata,
                                             max_depth=max_depth)
            metadata_html = metadata_table.to_html(with_headers=True,
                                                   with_newlines=with_newlines,
                                                   with_metadata=False,
                                                   max_depth=max_depth)
            if with_metadata != 'bottom':
                lines.append(metadata_html)
                lines.append('<br />')

        if with_headers and self.headers:
            headers.extend(self.headers)
            headers.extend([None] * (self._width - len(self.headers)))
        if wrapped:
            lines.append(self._html_table_tag)
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, headers=headers,
                                            max_depth=max_depth)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, headers=headers,
                                          max_depth=max_depth)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if with_metadata and self.metadata and with_metadata == 'bottom':
            lines.append('<br />')
            lines.append(metadata_html)

        if wrapped:
            lines.append(self._html_table_tag_close)
        sep = '\n' if with_newlines else ''
        return sep.join(None)
    
    xǁTableǁto_html__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁto_html__mutmut_1': xǁTableǁto_html__mutmut_1, 
        'xǁTableǁto_html__mutmut_2': xǁTableǁto_html__mutmut_2, 
        'xǁTableǁto_html__mutmut_3': xǁTableǁto_html__mutmut_3, 
        'xǁTableǁto_html__mutmut_4': xǁTableǁto_html__mutmut_4, 
        'xǁTableǁto_html__mutmut_5': xǁTableǁto_html__mutmut_5, 
        'xǁTableǁto_html__mutmut_6': xǁTableǁto_html__mutmut_6, 
        'xǁTableǁto_html__mutmut_7': xǁTableǁto_html__mutmut_7, 
        'xǁTableǁto_html__mutmut_8': xǁTableǁto_html__mutmut_8, 
        'xǁTableǁto_html__mutmut_9': xǁTableǁto_html__mutmut_9, 
        'xǁTableǁto_html__mutmut_10': xǁTableǁto_html__mutmut_10, 
        'xǁTableǁto_html__mutmut_11': xǁTableǁto_html__mutmut_11, 
        'xǁTableǁto_html__mutmut_12': xǁTableǁto_html__mutmut_12, 
        'xǁTableǁto_html__mutmut_13': xǁTableǁto_html__mutmut_13, 
        'xǁTableǁto_html__mutmut_14': xǁTableǁto_html__mutmut_14, 
        'xǁTableǁto_html__mutmut_15': xǁTableǁto_html__mutmut_15, 
        'xǁTableǁto_html__mutmut_16': xǁTableǁto_html__mutmut_16, 
        'xǁTableǁto_html__mutmut_17': xǁTableǁto_html__mutmut_17, 
        'xǁTableǁto_html__mutmut_18': xǁTableǁto_html__mutmut_18, 
        'xǁTableǁto_html__mutmut_19': xǁTableǁto_html__mutmut_19, 
        'xǁTableǁto_html__mutmut_20': xǁTableǁto_html__mutmut_20, 
        'xǁTableǁto_html__mutmut_21': xǁTableǁto_html__mutmut_21, 
        'xǁTableǁto_html__mutmut_22': xǁTableǁto_html__mutmut_22, 
        'xǁTableǁto_html__mutmut_23': xǁTableǁto_html__mutmut_23, 
        'xǁTableǁto_html__mutmut_24': xǁTableǁto_html__mutmut_24, 
        'xǁTableǁto_html__mutmut_25': xǁTableǁto_html__mutmut_25, 
        'xǁTableǁto_html__mutmut_26': xǁTableǁto_html__mutmut_26, 
        'xǁTableǁto_html__mutmut_27': xǁTableǁto_html__mutmut_27, 
        'xǁTableǁto_html__mutmut_28': xǁTableǁto_html__mutmut_28, 
        'xǁTableǁto_html__mutmut_29': xǁTableǁto_html__mutmut_29, 
        'xǁTableǁto_html__mutmut_30': xǁTableǁto_html__mutmut_30, 
        'xǁTableǁto_html__mutmut_31': xǁTableǁto_html__mutmut_31, 
        'xǁTableǁto_html__mutmut_32': xǁTableǁto_html__mutmut_32, 
        'xǁTableǁto_html__mutmut_33': xǁTableǁto_html__mutmut_33, 
        'xǁTableǁto_html__mutmut_34': xǁTableǁto_html__mutmut_34, 
        'xǁTableǁto_html__mutmut_35': xǁTableǁto_html__mutmut_35, 
        'xǁTableǁto_html__mutmut_36': xǁTableǁto_html__mutmut_36, 
        'xǁTableǁto_html__mutmut_37': xǁTableǁto_html__mutmut_37, 
        'xǁTableǁto_html__mutmut_38': xǁTableǁto_html__mutmut_38, 
        'xǁTableǁto_html__mutmut_39': xǁTableǁto_html__mutmut_39, 
        'xǁTableǁto_html__mutmut_40': xǁTableǁto_html__mutmut_40, 
        'xǁTableǁto_html__mutmut_41': xǁTableǁto_html__mutmut_41, 
        'xǁTableǁto_html__mutmut_42': xǁTableǁto_html__mutmut_42, 
        'xǁTableǁto_html__mutmut_43': xǁTableǁto_html__mutmut_43, 
        'xǁTableǁto_html__mutmut_44': xǁTableǁto_html__mutmut_44, 
        'xǁTableǁto_html__mutmut_45': xǁTableǁto_html__mutmut_45, 
        'xǁTableǁto_html__mutmut_46': xǁTableǁto_html__mutmut_46, 
        'xǁTableǁto_html__mutmut_47': xǁTableǁto_html__mutmut_47, 
        'xǁTableǁto_html__mutmut_48': xǁTableǁto_html__mutmut_48, 
        'xǁTableǁto_html__mutmut_49': xǁTableǁto_html__mutmut_49, 
        'xǁTableǁto_html__mutmut_50': xǁTableǁto_html__mutmut_50, 
        'xǁTableǁto_html__mutmut_51': xǁTableǁto_html__mutmut_51, 
        'xǁTableǁto_html__mutmut_52': xǁTableǁto_html__mutmut_52, 
        'xǁTableǁto_html__mutmut_53': xǁTableǁto_html__mutmut_53, 
        'xǁTableǁto_html__mutmut_54': xǁTableǁto_html__mutmut_54, 
        'xǁTableǁto_html__mutmut_55': xǁTableǁto_html__mutmut_55, 
        'xǁTableǁto_html__mutmut_56': xǁTableǁto_html__mutmut_56, 
        'xǁTableǁto_html__mutmut_57': xǁTableǁto_html__mutmut_57, 
        'xǁTableǁto_html__mutmut_58': xǁTableǁto_html__mutmut_58, 
        'xǁTableǁto_html__mutmut_59': xǁTableǁto_html__mutmut_59, 
        'xǁTableǁto_html__mutmut_60': xǁTableǁto_html__mutmut_60, 
        'xǁTableǁto_html__mutmut_61': xǁTableǁto_html__mutmut_61, 
        'xǁTableǁto_html__mutmut_62': xǁTableǁto_html__mutmut_62, 
        'xǁTableǁto_html__mutmut_63': xǁTableǁto_html__mutmut_63, 
        'xǁTableǁto_html__mutmut_64': xǁTableǁto_html__mutmut_64, 
        'xǁTableǁto_html__mutmut_65': xǁTableǁto_html__mutmut_65, 
        'xǁTableǁto_html__mutmut_66': xǁTableǁto_html__mutmut_66, 
        'xǁTableǁto_html__mutmut_67': xǁTableǁto_html__mutmut_67, 
        'xǁTableǁto_html__mutmut_68': xǁTableǁto_html__mutmut_68, 
        'xǁTableǁto_html__mutmut_69': xǁTableǁto_html__mutmut_69, 
        'xǁTableǁto_html__mutmut_70': xǁTableǁto_html__mutmut_70, 
        'xǁTableǁto_html__mutmut_71': xǁTableǁto_html__mutmut_71, 
        'xǁTableǁto_html__mutmut_72': xǁTableǁto_html__mutmut_72, 
        'xǁTableǁto_html__mutmut_73': xǁTableǁto_html__mutmut_73, 
        'xǁTableǁto_html__mutmut_74': xǁTableǁto_html__mutmut_74, 
        'xǁTableǁto_html__mutmut_75': xǁTableǁto_html__mutmut_75, 
        'xǁTableǁto_html__mutmut_76': xǁTableǁto_html__mutmut_76, 
        'xǁTableǁto_html__mutmut_77': xǁTableǁto_html__mutmut_77, 
        'xǁTableǁto_html__mutmut_78': xǁTableǁto_html__mutmut_78, 
        'xǁTableǁto_html__mutmut_79': xǁTableǁto_html__mutmut_79, 
        'xǁTableǁto_html__mutmut_80': xǁTableǁto_html__mutmut_80, 
        'xǁTableǁto_html__mutmut_81': xǁTableǁto_html__mutmut_81, 
        'xǁTableǁto_html__mutmut_82': xǁTableǁto_html__mutmut_82, 
        'xǁTableǁto_html__mutmut_83': xǁTableǁto_html__mutmut_83, 
        'xǁTableǁto_html__mutmut_84': xǁTableǁto_html__mutmut_84, 
        'xǁTableǁto_html__mutmut_85': xǁTableǁto_html__mutmut_85, 
        'xǁTableǁto_html__mutmut_86': xǁTableǁto_html__mutmut_86, 
        'xǁTableǁto_html__mutmut_87': xǁTableǁto_html__mutmut_87, 
        'xǁTableǁto_html__mutmut_88': xǁTableǁto_html__mutmut_88, 
        'xǁTableǁto_html__mutmut_89': xǁTableǁto_html__mutmut_89, 
        'xǁTableǁto_html__mutmut_90': xǁTableǁto_html__mutmut_90, 
        'xǁTableǁto_html__mutmut_91': xǁTableǁto_html__mutmut_91, 
        'xǁTableǁto_html__mutmut_92': xǁTableǁto_html__mutmut_92
    }
    
    def to_html(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁto_html__mutmut_orig"), object.__getattribute__(self, "xǁTableǁto_html__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_html.__signature__ = _mutmut_signature(xǁTableǁto_html__mutmut_orig)
    xǁTableǁto_html__mutmut_orig.__name__ = 'xǁTableǁto_html'

    def xǁTableǁget_cell_html__mutmut_orig(self, value):
        """Called on each value in an HTML table. By default it simply escapes
        the HTML. Override this method to add additional conditions
        and behaviors, but take care to ensure the final output is
        HTML escaped.
        """
        return escape_html(value)

    def xǁTableǁget_cell_html__mutmut_1(self, value):
        """Called on each value in an HTML table. By default it simply escapes
        the HTML. Override this method to add additional conditions
        and behaviors, but take care to ensure the final output is
        HTML escaped.
        """
        return escape_html(None)
    
    xǁTableǁget_cell_html__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁget_cell_html__mutmut_1': xǁTableǁget_cell_html__mutmut_1
    }
    
    def get_cell_html(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁget_cell_html__mutmut_orig"), object.__getattribute__(self, "xǁTableǁget_cell_html__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_cell_html.__signature__ = _mutmut_signature(xǁTableǁget_cell_html__mutmut_orig)
    xǁTableǁget_cell_html__mutmut_orig.__name__ = 'xǁTableǁget_cell_html'

    def xǁTableǁ_add_horizontal_html_lines__mutmut_orig(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_1(self, lines, headers, max_depth):
        esc = None
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_2(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = None
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_3(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth + 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_4(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 2 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_5(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth >= 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_6(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 2 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_7(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth >= 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_8(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 2:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_9(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = None
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_10(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth + 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_11(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 2
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_12(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = None
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_13(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close - self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_14(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(None)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_15(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(None)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_16(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close - self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_17(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) - self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_18(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th - _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_19(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr - self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_20(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join(None) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_21(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(None) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_22(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(None)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_23(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = None
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_24(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr - self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_25(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close - self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_26(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close - self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_27(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(None)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_28(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth >= 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_29(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 2:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_30(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = None
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_31(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(None)
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_32(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=None))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_33(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(None)
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_34(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(None))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_35(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = None
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_36(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(None) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_37(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(None)
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_38(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join(None))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_39(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append('XXXX'.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_40(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(None), _td_tr]))
        lines.append(self._html_tbody_close)

    def xǁTableǁ_add_horizontal_html_lines__mutmut_41(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        if max_depth > 1:
            new_depth = max_depth - 1
        if headers:
            _thth = self._html_th_close + self._html_th
            lines.append(self._html_thead)
            lines.append(self._html_tr + self._html_th +
                         _thth.join([esc(h) for h in headers]) +
                         self._html_th_close + self._html_tr_close)
            lines.append(self._html_thead_close)
        trtd, _tdtd, _td_tr = (self._html_tr + self._html_td,
                               self._html_td_close + self._html_td,
                               self._html_td_close + self._html_tr_close)
        lines.append(self._html_tbody)
        for row in self._data:
            if max_depth > 1:
                _fill_parts = []
                for cell in row:
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(cell))
            else:
                _fill_parts = [esc(c) for c in row]
            lines.append(''.join([trtd, _tdtd.join(_fill_parts), _td_tr]))
        lines.append(None)
    
    xǁTableǁ_add_horizontal_html_lines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ_add_horizontal_html_lines__mutmut_1': xǁTableǁ_add_horizontal_html_lines__mutmut_1, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_2': xǁTableǁ_add_horizontal_html_lines__mutmut_2, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_3': xǁTableǁ_add_horizontal_html_lines__mutmut_3, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_4': xǁTableǁ_add_horizontal_html_lines__mutmut_4, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_5': xǁTableǁ_add_horizontal_html_lines__mutmut_5, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_6': xǁTableǁ_add_horizontal_html_lines__mutmut_6, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_7': xǁTableǁ_add_horizontal_html_lines__mutmut_7, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_8': xǁTableǁ_add_horizontal_html_lines__mutmut_8, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_9': xǁTableǁ_add_horizontal_html_lines__mutmut_9, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_10': xǁTableǁ_add_horizontal_html_lines__mutmut_10, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_11': xǁTableǁ_add_horizontal_html_lines__mutmut_11, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_12': xǁTableǁ_add_horizontal_html_lines__mutmut_12, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_13': xǁTableǁ_add_horizontal_html_lines__mutmut_13, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_14': xǁTableǁ_add_horizontal_html_lines__mutmut_14, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_15': xǁTableǁ_add_horizontal_html_lines__mutmut_15, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_16': xǁTableǁ_add_horizontal_html_lines__mutmut_16, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_17': xǁTableǁ_add_horizontal_html_lines__mutmut_17, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_18': xǁTableǁ_add_horizontal_html_lines__mutmut_18, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_19': xǁTableǁ_add_horizontal_html_lines__mutmut_19, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_20': xǁTableǁ_add_horizontal_html_lines__mutmut_20, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_21': xǁTableǁ_add_horizontal_html_lines__mutmut_21, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_22': xǁTableǁ_add_horizontal_html_lines__mutmut_22, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_23': xǁTableǁ_add_horizontal_html_lines__mutmut_23, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_24': xǁTableǁ_add_horizontal_html_lines__mutmut_24, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_25': xǁTableǁ_add_horizontal_html_lines__mutmut_25, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_26': xǁTableǁ_add_horizontal_html_lines__mutmut_26, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_27': xǁTableǁ_add_horizontal_html_lines__mutmut_27, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_28': xǁTableǁ_add_horizontal_html_lines__mutmut_28, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_29': xǁTableǁ_add_horizontal_html_lines__mutmut_29, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_30': xǁTableǁ_add_horizontal_html_lines__mutmut_30, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_31': xǁTableǁ_add_horizontal_html_lines__mutmut_31, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_32': xǁTableǁ_add_horizontal_html_lines__mutmut_32, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_33': xǁTableǁ_add_horizontal_html_lines__mutmut_33, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_34': xǁTableǁ_add_horizontal_html_lines__mutmut_34, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_35': xǁTableǁ_add_horizontal_html_lines__mutmut_35, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_36': xǁTableǁ_add_horizontal_html_lines__mutmut_36, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_37': xǁTableǁ_add_horizontal_html_lines__mutmut_37, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_38': xǁTableǁ_add_horizontal_html_lines__mutmut_38, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_39': xǁTableǁ_add_horizontal_html_lines__mutmut_39, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_40': xǁTableǁ_add_horizontal_html_lines__mutmut_40, 
        'xǁTableǁ_add_horizontal_html_lines__mutmut_41': xǁTableǁ_add_horizontal_html_lines__mutmut_41
    }
    
    def _add_horizontal_html_lines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ_add_horizontal_html_lines__mutmut_orig"), object.__getattribute__(self, "xǁTableǁ_add_horizontal_html_lines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _add_horizontal_html_lines.__signature__ = _mutmut_signature(xǁTableǁ_add_horizontal_html_lines__mutmut_orig)
    xǁTableǁ_add_horizontal_html_lines__mutmut_orig.__name__ = 'xǁTableǁ_add_horizontal_html_lines'

    def xǁTableǁ_add_vertical_html_lines__mutmut_orig(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_1(self, lines, headers, max_depth):
        esc = None
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_2(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = None
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_3(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth + 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_4(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 2 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_5(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth >= 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_6(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 2 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_7(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = None
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_8(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = None
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_9(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close - self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_10(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = None
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_11(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close - self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_12(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(None):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_13(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = None
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_14(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend(None)
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_15(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(None), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_16(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth >= 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_17(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 2:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_18(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = None
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_19(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth + 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_20(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 2
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_21(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = None
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_22(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = None
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_23(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(None)
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_24(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=None))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_25(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(None)
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_26(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(None))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_27(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = None
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_28(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(None) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_29(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend(None)
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_30(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(None), _td_tr])
            lines.append(''.join(line_parts))

    def xǁTableǁ_add_vertical_html_lines__mutmut_31(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(None)

    def xǁTableǁ_add_vertical_html_lines__mutmut_32(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append(''.join(None))

    def xǁTableǁ_add_vertical_html_lines__mutmut_33(self, lines, headers, max_depth):
        esc = self.get_cell_html
        new_depth = max_depth - 1 if max_depth > 1 else max_depth
        tr, th, _th = self._html_tr, self._html_th, self._html_th_close
        td, _tdtd = self._html_td, self._html_td_close + self._html_td
        _td_tr = self._html_td_close + self._html_tr_close
        for i in range(self._width):
            line_parts = [tr]
            if headers:
                line_parts.extend([th, esc(headers[i]), _th])
            if max_depth > 1:
                new_depth = max_depth - 1
                _fill_parts = []
                for row in self._data:
                    cell = row[i]
                    if isinstance(cell, Table):
                        _fill_parts.append(cell.to_html(max_depth=new_depth))
                    else:
                        _fill_parts.append(esc(row[i]))
            else:
                _fill_parts = [esc(row[i]) for row in self._data]
            line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
            lines.append('XXXX'.join(line_parts))
    
    xǁTableǁ_add_vertical_html_lines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁ_add_vertical_html_lines__mutmut_1': xǁTableǁ_add_vertical_html_lines__mutmut_1, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_2': xǁTableǁ_add_vertical_html_lines__mutmut_2, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_3': xǁTableǁ_add_vertical_html_lines__mutmut_3, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_4': xǁTableǁ_add_vertical_html_lines__mutmut_4, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_5': xǁTableǁ_add_vertical_html_lines__mutmut_5, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_6': xǁTableǁ_add_vertical_html_lines__mutmut_6, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_7': xǁTableǁ_add_vertical_html_lines__mutmut_7, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_8': xǁTableǁ_add_vertical_html_lines__mutmut_8, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_9': xǁTableǁ_add_vertical_html_lines__mutmut_9, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_10': xǁTableǁ_add_vertical_html_lines__mutmut_10, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_11': xǁTableǁ_add_vertical_html_lines__mutmut_11, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_12': xǁTableǁ_add_vertical_html_lines__mutmut_12, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_13': xǁTableǁ_add_vertical_html_lines__mutmut_13, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_14': xǁTableǁ_add_vertical_html_lines__mutmut_14, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_15': xǁTableǁ_add_vertical_html_lines__mutmut_15, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_16': xǁTableǁ_add_vertical_html_lines__mutmut_16, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_17': xǁTableǁ_add_vertical_html_lines__mutmut_17, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_18': xǁTableǁ_add_vertical_html_lines__mutmut_18, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_19': xǁTableǁ_add_vertical_html_lines__mutmut_19, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_20': xǁTableǁ_add_vertical_html_lines__mutmut_20, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_21': xǁTableǁ_add_vertical_html_lines__mutmut_21, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_22': xǁTableǁ_add_vertical_html_lines__mutmut_22, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_23': xǁTableǁ_add_vertical_html_lines__mutmut_23, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_24': xǁTableǁ_add_vertical_html_lines__mutmut_24, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_25': xǁTableǁ_add_vertical_html_lines__mutmut_25, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_26': xǁTableǁ_add_vertical_html_lines__mutmut_26, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_27': xǁTableǁ_add_vertical_html_lines__mutmut_27, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_28': xǁTableǁ_add_vertical_html_lines__mutmut_28, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_29': xǁTableǁ_add_vertical_html_lines__mutmut_29, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_30': xǁTableǁ_add_vertical_html_lines__mutmut_30, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_31': xǁTableǁ_add_vertical_html_lines__mutmut_31, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_32': xǁTableǁ_add_vertical_html_lines__mutmut_32, 
        'xǁTableǁ_add_vertical_html_lines__mutmut_33': xǁTableǁ_add_vertical_html_lines__mutmut_33
    }
    
    def _add_vertical_html_lines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁ_add_vertical_html_lines__mutmut_orig"), object.__getattribute__(self, "xǁTableǁ_add_vertical_html_lines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _add_vertical_html_lines.__signature__ = _mutmut_signature(xǁTableǁ_add_vertical_html_lines__mutmut_orig)
    xǁTableǁ_add_vertical_html_lines__mutmut_orig.__name__ = 'xǁTableǁ_add_vertical_html_lines'

    def xǁTableǁto_text__mutmut_orig(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_1(self, with_headers=False, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_2(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = None
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_3(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = None
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_4(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = None
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_5(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(None)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_6(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = None
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_7(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(None, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_8(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=None) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_9(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_10(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, ) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_11(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(None):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_12(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = None
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_13(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(None)
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_14(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(None)
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_15(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(None))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_16(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(None)
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_17(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join(None))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_18(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append('XX | XX'.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_19(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(None)
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_20(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(None)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_21(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append(None)
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_22(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(None))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_23(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('XX-|-XX'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_24(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' / w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_25(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['XX-XX' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_26(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(None)
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_27(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join(None))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_28(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append('XX | XX'.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_29(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(None)
                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_30(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(None)]))
        return '\n'.join(lines)

    def xǁTableǁto_text__mutmut_31(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return '\n'.join(None)

    def xǁTableǁto_text__mutmut_32(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.

        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
            widths.append(max(cur_widths))
        if with_headers:
            lines.append(' | '.join([h.center(widths[i])
                                     for i, h in enumerate(headers)]))
            lines.append('-|-'.join(['-' * w for w in widths]))
        for row in text_data:
            lines.append(' | '.join([cell.center(widths[j])
                                     for j, cell in enumerate(row)]))
        return 'XX\nXX'.join(lines)
    
    xǁTableǁto_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTableǁto_text__mutmut_1': xǁTableǁto_text__mutmut_1, 
        'xǁTableǁto_text__mutmut_2': xǁTableǁto_text__mutmut_2, 
        'xǁTableǁto_text__mutmut_3': xǁTableǁto_text__mutmut_3, 
        'xǁTableǁto_text__mutmut_4': xǁTableǁto_text__mutmut_4, 
        'xǁTableǁto_text__mutmut_5': xǁTableǁto_text__mutmut_5, 
        'xǁTableǁto_text__mutmut_6': xǁTableǁto_text__mutmut_6, 
        'xǁTableǁto_text__mutmut_7': xǁTableǁto_text__mutmut_7, 
        'xǁTableǁto_text__mutmut_8': xǁTableǁto_text__mutmut_8, 
        'xǁTableǁto_text__mutmut_9': xǁTableǁto_text__mutmut_9, 
        'xǁTableǁto_text__mutmut_10': xǁTableǁto_text__mutmut_10, 
        'xǁTableǁto_text__mutmut_11': xǁTableǁto_text__mutmut_11, 
        'xǁTableǁto_text__mutmut_12': xǁTableǁto_text__mutmut_12, 
        'xǁTableǁto_text__mutmut_13': xǁTableǁto_text__mutmut_13, 
        'xǁTableǁto_text__mutmut_14': xǁTableǁto_text__mutmut_14, 
        'xǁTableǁto_text__mutmut_15': xǁTableǁto_text__mutmut_15, 
        'xǁTableǁto_text__mutmut_16': xǁTableǁto_text__mutmut_16, 
        'xǁTableǁto_text__mutmut_17': xǁTableǁto_text__mutmut_17, 
        'xǁTableǁto_text__mutmut_18': xǁTableǁto_text__mutmut_18, 
        'xǁTableǁto_text__mutmut_19': xǁTableǁto_text__mutmut_19, 
        'xǁTableǁto_text__mutmut_20': xǁTableǁto_text__mutmut_20, 
        'xǁTableǁto_text__mutmut_21': xǁTableǁto_text__mutmut_21, 
        'xǁTableǁto_text__mutmut_22': xǁTableǁto_text__mutmut_22, 
        'xǁTableǁto_text__mutmut_23': xǁTableǁto_text__mutmut_23, 
        'xǁTableǁto_text__mutmut_24': xǁTableǁto_text__mutmut_24, 
        'xǁTableǁto_text__mutmut_25': xǁTableǁto_text__mutmut_25, 
        'xǁTableǁto_text__mutmut_26': xǁTableǁto_text__mutmut_26, 
        'xǁTableǁto_text__mutmut_27': xǁTableǁto_text__mutmut_27, 
        'xǁTableǁto_text__mutmut_28': xǁTableǁto_text__mutmut_28, 
        'xǁTableǁto_text__mutmut_29': xǁTableǁto_text__mutmut_29, 
        'xǁTableǁto_text__mutmut_30': xǁTableǁto_text__mutmut_30, 
        'xǁTableǁto_text__mutmut_31': xǁTableǁto_text__mutmut_31, 
        'xǁTableǁto_text__mutmut_32': xǁTableǁto_text__mutmut_32
    }
    
    def to_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTableǁto_text__mutmut_orig"), object.__getattribute__(self, "xǁTableǁto_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_text.__signature__ = _mutmut_signature(xǁTableǁto_text__mutmut_orig)
    xǁTableǁto_text__mutmut_orig.__name__ = 'xǁTableǁto_text'
