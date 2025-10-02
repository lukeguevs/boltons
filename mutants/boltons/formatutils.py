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

"""`PEP 3101`_ introduced the :meth:`str.format` method, and what
would later be called "new-style" string formatting. For the sake of
explicit correctness, it is probably best to refer to Python's dual
string formatting capabilities as *bracket-style* and
*percent-style*. There is overlap, but one does not replace the
other.

  * Bracket-style is more pluggable, slower, and uses a method.
  * Percent-style is simpler, faster, and uses an operator.

Bracket-style formatting brought with it a much more powerful toolbox,
but it was far from a full one. :meth:`str.format` uses `more powerful
syntax`_, but `the tools and idioms`_ for working with
that syntax are not well-developed nor well-advertised.

``formatutils`` adds several functions for working with bracket-style
format strings:

  * :class:`DeferredValue`: Defer fetching or calculating a value
    until format time.
  * :func:`get_format_args`: Parse the positional and keyword
    arguments out of a format string.
  * :func:`tokenize_format_str`: Tokenize a format string into
    literals and :class:`BaseFormatField` objects.
  * :func:`construct_format_field_str`: Assists in programmatic
    construction of format strings.
  * :func:`infer_positional_format_args`: Converts anonymous
    references in 2.7+ format strings to explicit positional arguments
    suitable for usage with Python 2.6.

.. _more powerful syntax: https://docs.python.org/2/library/string.html#format-string-syntax
.. _the tools and idioms: https://docs.python.org/2/library/string.html#string-formatting
.. _PEP 3101: https://www.python.org/dev/peps/pep-3101/
"""
# TODO: also include percent-formatting utils?
# TODO: include lithoxyl.formatters.Formatter (or some adaptation)?


import re
from string import Formatter

__all__ = ['DeferredValue', 'get_format_args', 'tokenize_format_str',
           'construct_format_field_str', 'infer_positional_format_args',
           'BaseFormatField']


_pos_farg_re = re.compile('({{)|'         # escaped open-brace
                          '(}})|'         # escaped close-brace
                          r'({[:!.\[}])')  # anon positional format arg
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


def x_construct_format_field_str__mutmut_orig(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_1(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is not None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_2(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return 'XXXX'
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_3(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = None
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_4(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' - fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_5(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = 'XX{XX' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_6(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret = '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_7(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret -= '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_8(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' - conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_9(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += 'XX!XX' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_10(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret = ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_11(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret -= ':' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_12(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' - fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_13(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += 'XX:XX' + fspec
    ret += '}'
    return ret


def x_construct_format_field_str__mutmut_14(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret = '}'
    return ret


def x_construct_format_field_str__mutmut_15(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret -= '}'
    return ret


def x_construct_format_field_str__mutmut_16(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += 'XX}XX'
    return ret

x_construct_format_field_str__mutmut_mutants : ClassVar[MutantDict] = {
'x_construct_format_field_str__mutmut_1': x_construct_format_field_str__mutmut_1, 
    'x_construct_format_field_str__mutmut_2': x_construct_format_field_str__mutmut_2, 
    'x_construct_format_field_str__mutmut_3': x_construct_format_field_str__mutmut_3, 
    'x_construct_format_field_str__mutmut_4': x_construct_format_field_str__mutmut_4, 
    'x_construct_format_field_str__mutmut_5': x_construct_format_field_str__mutmut_5, 
    'x_construct_format_field_str__mutmut_6': x_construct_format_field_str__mutmut_6, 
    'x_construct_format_field_str__mutmut_7': x_construct_format_field_str__mutmut_7, 
    'x_construct_format_field_str__mutmut_8': x_construct_format_field_str__mutmut_8, 
    'x_construct_format_field_str__mutmut_9': x_construct_format_field_str__mutmut_9, 
    'x_construct_format_field_str__mutmut_10': x_construct_format_field_str__mutmut_10, 
    'x_construct_format_field_str__mutmut_11': x_construct_format_field_str__mutmut_11, 
    'x_construct_format_field_str__mutmut_12': x_construct_format_field_str__mutmut_12, 
    'x_construct_format_field_str__mutmut_13': x_construct_format_field_str__mutmut_13, 
    'x_construct_format_field_str__mutmut_14': x_construct_format_field_str__mutmut_14, 
    'x_construct_format_field_str__mutmut_15': x_construct_format_field_str__mutmut_15, 
    'x_construct_format_field_str__mutmut_16': x_construct_format_field_str__mutmut_16
}

def construct_format_field_str(*args, **kwargs):
    result = _mutmut_trampoline(x_construct_format_field_str__mutmut_orig, x_construct_format_field_str__mutmut_mutants, args, kwargs)
    return result 

construct_format_field_str.__signature__ = _mutmut_signature(x_construct_format_field_str__mutmut_orig)
x_construct_format_field_str__mutmut_orig.__name__ = 'x_construct_format_field_str'


def x_split_format_str__mutmut_orig(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_1(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = None

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_2(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(None):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_3(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is not None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_4(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append(None)
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_5(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            break
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_6(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = None
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_7(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(None, fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_8(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, None, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_9(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, None)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_10(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fspec, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_11(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, conv)
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_12(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, )
        ret.append((lit, field_str))
    return ret


def x_split_format_str__mutmut_13(fstr):
    """Does very basic splitting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.

    """
    ret = []

    for lit, fname, fspec, conv in Formatter().parse(fstr):
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append(None)
    return ret

x_split_format_str__mutmut_mutants : ClassVar[MutantDict] = {
'x_split_format_str__mutmut_1': x_split_format_str__mutmut_1, 
    'x_split_format_str__mutmut_2': x_split_format_str__mutmut_2, 
    'x_split_format_str__mutmut_3': x_split_format_str__mutmut_3, 
    'x_split_format_str__mutmut_4': x_split_format_str__mutmut_4, 
    'x_split_format_str__mutmut_5': x_split_format_str__mutmut_5, 
    'x_split_format_str__mutmut_6': x_split_format_str__mutmut_6, 
    'x_split_format_str__mutmut_7': x_split_format_str__mutmut_7, 
    'x_split_format_str__mutmut_8': x_split_format_str__mutmut_8, 
    'x_split_format_str__mutmut_9': x_split_format_str__mutmut_9, 
    'x_split_format_str__mutmut_10': x_split_format_str__mutmut_10, 
    'x_split_format_str__mutmut_11': x_split_format_str__mutmut_11, 
    'x_split_format_str__mutmut_12': x_split_format_str__mutmut_12, 
    'x_split_format_str__mutmut_13': x_split_format_str__mutmut_13
}

def split_format_str(*args, **kwargs):
    result = _mutmut_trampoline(x_split_format_str__mutmut_orig, x_split_format_str__mutmut_mutants, args, kwargs)
    return result 

split_format_str.__signature__ = _mutmut_signature(x_split_format_str__mutmut_orig)
x_split_format_str__mutmut_orig.__name__ = 'x_split_format_str'


def x_infer_positional_format_args__mutmut_orig(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_1(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = None
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_2(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = 'XXXX', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_3(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 1
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_4(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = None
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_5(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 1, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_6(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 1, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_7(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 1
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_8(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(None):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_9(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = None
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_10(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end <= start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_11(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret = fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_12(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret -= fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_13(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = None
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_14(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' and group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_15(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group != '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_16(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == 'XX{{XX' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_17(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group != '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_18(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == 'XX}}XX':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_19(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret = group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_20(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret -= group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_21(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            break
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_22(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret = f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_23(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret -= f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_24(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[2:]}'
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_25(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon = 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_26(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon -= 1
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_27(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 2
    ret += fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_28(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret = fstr[prev_end:]
    return ret


def x_infer_positional_format_args__mutmut_29(fstr):
    """Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += f'{{{max_anon}{group[1:]}'
        max_anon += 1
    ret -= fstr[prev_end:]
    return ret

x_infer_positional_format_args__mutmut_mutants : ClassVar[MutantDict] = {
'x_infer_positional_format_args__mutmut_1': x_infer_positional_format_args__mutmut_1, 
    'x_infer_positional_format_args__mutmut_2': x_infer_positional_format_args__mutmut_2, 
    'x_infer_positional_format_args__mutmut_3': x_infer_positional_format_args__mutmut_3, 
    'x_infer_positional_format_args__mutmut_4': x_infer_positional_format_args__mutmut_4, 
    'x_infer_positional_format_args__mutmut_5': x_infer_positional_format_args__mutmut_5, 
    'x_infer_positional_format_args__mutmut_6': x_infer_positional_format_args__mutmut_6, 
    'x_infer_positional_format_args__mutmut_7': x_infer_positional_format_args__mutmut_7, 
    'x_infer_positional_format_args__mutmut_8': x_infer_positional_format_args__mutmut_8, 
    'x_infer_positional_format_args__mutmut_9': x_infer_positional_format_args__mutmut_9, 
    'x_infer_positional_format_args__mutmut_10': x_infer_positional_format_args__mutmut_10, 
    'x_infer_positional_format_args__mutmut_11': x_infer_positional_format_args__mutmut_11, 
    'x_infer_positional_format_args__mutmut_12': x_infer_positional_format_args__mutmut_12, 
    'x_infer_positional_format_args__mutmut_13': x_infer_positional_format_args__mutmut_13, 
    'x_infer_positional_format_args__mutmut_14': x_infer_positional_format_args__mutmut_14, 
    'x_infer_positional_format_args__mutmut_15': x_infer_positional_format_args__mutmut_15, 
    'x_infer_positional_format_args__mutmut_16': x_infer_positional_format_args__mutmut_16, 
    'x_infer_positional_format_args__mutmut_17': x_infer_positional_format_args__mutmut_17, 
    'x_infer_positional_format_args__mutmut_18': x_infer_positional_format_args__mutmut_18, 
    'x_infer_positional_format_args__mutmut_19': x_infer_positional_format_args__mutmut_19, 
    'x_infer_positional_format_args__mutmut_20': x_infer_positional_format_args__mutmut_20, 
    'x_infer_positional_format_args__mutmut_21': x_infer_positional_format_args__mutmut_21, 
    'x_infer_positional_format_args__mutmut_22': x_infer_positional_format_args__mutmut_22, 
    'x_infer_positional_format_args__mutmut_23': x_infer_positional_format_args__mutmut_23, 
    'x_infer_positional_format_args__mutmut_24': x_infer_positional_format_args__mutmut_24, 
    'x_infer_positional_format_args__mutmut_25': x_infer_positional_format_args__mutmut_25, 
    'x_infer_positional_format_args__mutmut_26': x_infer_positional_format_args__mutmut_26, 
    'x_infer_positional_format_args__mutmut_27': x_infer_positional_format_args__mutmut_27, 
    'x_infer_positional_format_args__mutmut_28': x_infer_positional_format_args__mutmut_28, 
    'x_infer_positional_format_args__mutmut_29': x_infer_positional_format_args__mutmut_29
}

def infer_positional_format_args(*args, **kwargs):
    result = _mutmut_trampoline(x_infer_positional_format_args__mutmut_orig, x_infer_positional_format_args__mutmut_mutants, args, kwargs)
    return result 

infer_positional_format_args.__signature__ = _mutmut_signature(x_infer_positional_format_args__mutmut_orig)
x_infer_positional_format_args__mutmut_orig.__name__ = 'x_infer_positional_format_args'


# This approach is hardly exhaustive but it works for most builtins
_INTCHARS = 'bcdoxXn'
_FLOATCHARS = 'eEfFgGn%'
_TYPE_MAP = dict([(x, int) for x in _INTCHARS] +
                 [(x, float) for x in _FLOATCHARS])
_TYPE_MAP['s'] = str


def x_get_format_args__mutmut_orig(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_1(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = None
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_2(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = None

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_3(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='XXsXX'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_4(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='S'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_5(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_6(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(None)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_7(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = None  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_8(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(None, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_9(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, None)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_10(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_11(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, )  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_12(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append(None)
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_13(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(None), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_14(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append(None)

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_15(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(None):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_16(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_17(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = None
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_18(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[+1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_19(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-2:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_20(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = None
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_21(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split(None, fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_22(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', None)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_23(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split(fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_24(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', )
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_25(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.rsplit('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_26(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('XX[.[]XX', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_27(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) >= 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_28(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 2:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_29(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError(None)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_30(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' / fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_31(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('XXencountered compound format arg: %rXX' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_32(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('ENCOUNTERED COMPOUND FORMAT ARG: %R' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_33(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = None
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_34(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[1]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_35(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError(None)
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_36(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('XXencountered anonymous positional argumentXX')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_37(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('ENCOUNTERED ANONYMOUS POSITIONAL ARGUMENT')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_38(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(None, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_39(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, None)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_40(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_41(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, )
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_42(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(None):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_43(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is None:
                    _add_arg(subfname)
    return fargs, fkwargs


def x_get_format_args__mutmut_44(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    # >>> get_format_args("{noun} is {1:d} years old{punct}")
    # ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])

    # XXX: Py3k
    >>> get_format_args("{noun} is {1:d} years old{punct}") == \
        ([(1, int)], [('noun', str), ('punct', str)])
    True
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(None)
    return fargs, fkwargs

x_get_format_args__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_format_args__mutmut_1': x_get_format_args__mutmut_1, 
    'x_get_format_args__mutmut_2': x_get_format_args__mutmut_2, 
    'x_get_format_args__mutmut_3': x_get_format_args__mutmut_3, 
    'x_get_format_args__mutmut_4': x_get_format_args__mutmut_4, 
    'x_get_format_args__mutmut_5': x_get_format_args__mutmut_5, 
    'x_get_format_args__mutmut_6': x_get_format_args__mutmut_6, 
    'x_get_format_args__mutmut_7': x_get_format_args__mutmut_7, 
    'x_get_format_args__mutmut_8': x_get_format_args__mutmut_8, 
    'x_get_format_args__mutmut_9': x_get_format_args__mutmut_9, 
    'x_get_format_args__mutmut_10': x_get_format_args__mutmut_10, 
    'x_get_format_args__mutmut_11': x_get_format_args__mutmut_11, 
    'x_get_format_args__mutmut_12': x_get_format_args__mutmut_12, 
    'x_get_format_args__mutmut_13': x_get_format_args__mutmut_13, 
    'x_get_format_args__mutmut_14': x_get_format_args__mutmut_14, 
    'x_get_format_args__mutmut_15': x_get_format_args__mutmut_15, 
    'x_get_format_args__mutmut_16': x_get_format_args__mutmut_16, 
    'x_get_format_args__mutmut_17': x_get_format_args__mutmut_17, 
    'x_get_format_args__mutmut_18': x_get_format_args__mutmut_18, 
    'x_get_format_args__mutmut_19': x_get_format_args__mutmut_19, 
    'x_get_format_args__mutmut_20': x_get_format_args__mutmut_20, 
    'x_get_format_args__mutmut_21': x_get_format_args__mutmut_21, 
    'x_get_format_args__mutmut_22': x_get_format_args__mutmut_22, 
    'x_get_format_args__mutmut_23': x_get_format_args__mutmut_23, 
    'x_get_format_args__mutmut_24': x_get_format_args__mutmut_24, 
    'x_get_format_args__mutmut_25': x_get_format_args__mutmut_25, 
    'x_get_format_args__mutmut_26': x_get_format_args__mutmut_26, 
    'x_get_format_args__mutmut_27': x_get_format_args__mutmut_27, 
    'x_get_format_args__mutmut_28': x_get_format_args__mutmut_28, 
    'x_get_format_args__mutmut_29': x_get_format_args__mutmut_29, 
    'x_get_format_args__mutmut_30': x_get_format_args__mutmut_30, 
    'x_get_format_args__mutmut_31': x_get_format_args__mutmut_31, 
    'x_get_format_args__mutmut_32': x_get_format_args__mutmut_32, 
    'x_get_format_args__mutmut_33': x_get_format_args__mutmut_33, 
    'x_get_format_args__mutmut_34': x_get_format_args__mutmut_34, 
    'x_get_format_args__mutmut_35': x_get_format_args__mutmut_35, 
    'x_get_format_args__mutmut_36': x_get_format_args__mutmut_36, 
    'x_get_format_args__mutmut_37': x_get_format_args__mutmut_37, 
    'x_get_format_args__mutmut_38': x_get_format_args__mutmut_38, 
    'x_get_format_args__mutmut_39': x_get_format_args__mutmut_39, 
    'x_get_format_args__mutmut_40': x_get_format_args__mutmut_40, 
    'x_get_format_args__mutmut_41': x_get_format_args__mutmut_41, 
    'x_get_format_args__mutmut_42': x_get_format_args__mutmut_42, 
    'x_get_format_args__mutmut_43': x_get_format_args__mutmut_43, 
    'x_get_format_args__mutmut_44': x_get_format_args__mutmut_44
}

def get_format_args(*args, **kwargs):
    result = _mutmut_trampoline(x_get_format_args__mutmut_orig, x_get_format_args__mutmut_mutants, args, kwargs)
    return result 

get_format_args.__signature__ = _mutmut_signature(x_get_format_args__mutmut_orig)
x_get_format_args__mutmut_orig.__name__ = 'x_get_format_args'


def x_tokenize_format_str__mutmut_orig(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_1(fstr, resolve_pos=False):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_2(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = None
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_3(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = None
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_4(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(None)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_5(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = None
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_6(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(None):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_7(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(None)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_8(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is not None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_9(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            break
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_10(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(None)
    return ret


def x_tokenize_format_str__mutmut_11(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(None, fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_12(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, None, conv))
    return ret


def x_tokenize_format_str__mutmut_13(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, None))
    return ret


def x_tokenize_format_str__mutmut_14(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fspec, conv))
    return ret


def x_tokenize_format_str__mutmut_15(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, conv))
    return ret


def x_tokenize_format_str__mutmut_16(fstr, resolve_pos=True):
    """Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explicit, numbered
    positional references. To disable this behavior set *resolve_pos*
    to ``False``.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, ))
    return ret

x_tokenize_format_str__mutmut_mutants : ClassVar[MutantDict] = {
'x_tokenize_format_str__mutmut_1': x_tokenize_format_str__mutmut_1, 
    'x_tokenize_format_str__mutmut_2': x_tokenize_format_str__mutmut_2, 
    'x_tokenize_format_str__mutmut_3': x_tokenize_format_str__mutmut_3, 
    'x_tokenize_format_str__mutmut_4': x_tokenize_format_str__mutmut_4, 
    'x_tokenize_format_str__mutmut_5': x_tokenize_format_str__mutmut_5, 
    'x_tokenize_format_str__mutmut_6': x_tokenize_format_str__mutmut_6, 
    'x_tokenize_format_str__mutmut_7': x_tokenize_format_str__mutmut_7, 
    'x_tokenize_format_str__mutmut_8': x_tokenize_format_str__mutmut_8, 
    'x_tokenize_format_str__mutmut_9': x_tokenize_format_str__mutmut_9, 
    'x_tokenize_format_str__mutmut_10': x_tokenize_format_str__mutmut_10, 
    'x_tokenize_format_str__mutmut_11': x_tokenize_format_str__mutmut_11, 
    'x_tokenize_format_str__mutmut_12': x_tokenize_format_str__mutmut_12, 
    'x_tokenize_format_str__mutmut_13': x_tokenize_format_str__mutmut_13, 
    'x_tokenize_format_str__mutmut_14': x_tokenize_format_str__mutmut_14, 
    'x_tokenize_format_str__mutmut_15': x_tokenize_format_str__mutmut_15, 
    'x_tokenize_format_str__mutmut_16': x_tokenize_format_str__mutmut_16
}

def tokenize_format_str(*args, **kwargs):
    result = _mutmut_trampoline(x_tokenize_format_str__mutmut_orig, x_tokenize_format_str__mutmut_mutants, args, kwargs)
    return result 

tokenize_format_str.__signature__ = _mutmut_signature(x_tokenize_format_str__mutmut_orig)
x_tokenize_format_str__mutmut_orig.__name__ = 'x_tokenize_format_str'


class BaseFormatField:
    """A class representing a reference to an argument inside of a
    bracket-style format string. For instance, in ``"{greeting},
    world!"``, there is a field named "greeting".

    These fields can have many options applied to them. See the
    Python docs on `Format String Syntax`_ for the full details.

    .. _Format String Syntax: https://docs.python.org/2/library/string.html#string-formatting
    """
    def xǁBaseFormatFieldǁ__init____mutmut_orig(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(conv)
    def xǁBaseFormatFieldǁ__init____mutmut_1(self, fname, fspec='XXXX', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(conv)
    def xǁBaseFormatFieldǁ__init____mutmut_2(self, fname, fspec='', conv=None):
        self.set_fname(None)
        self.set_fspec(fspec)
        self.set_conv(conv)
    def xǁBaseFormatFieldǁ__init____mutmut_3(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(None)
        self.set_conv(conv)
    def xǁBaseFormatFieldǁ__init____mutmut_4(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(None)
    
    xǁBaseFormatFieldǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseFormatFieldǁ__init____mutmut_1': xǁBaseFormatFieldǁ__init____mutmut_1, 
        'xǁBaseFormatFieldǁ__init____mutmut_2': xǁBaseFormatFieldǁ__init____mutmut_2, 
        'xǁBaseFormatFieldǁ__init____mutmut_3': xǁBaseFormatFieldǁ__init____mutmut_3, 
        'xǁBaseFormatFieldǁ__init____mutmut_4': xǁBaseFormatFieldǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseFormatFieldǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBaseFormatFieldǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBaseFormatFieldǁ__init____mutmut_orig)
    xǁBaseFormatFieldǁ__init____mutmut_orig.__name__ = 'xǁBaseFormatFieldǁ__init__'

    def xǁBaseFormatFieldǁset_fname__mutmut_orig(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_1(self, fname):
        "XXSet the field name.XX"

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_2(self, fname):
        "set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_3(self, fname):
        "SET THE FIELD NAME."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_4(self, fname):
        "Set the field name."

        path_list = None  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_5(self, fname):
        "Set the field name."

        path_list = re.split(None, fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_6(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', None)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_7(self, fname):
        "Set the field name."

        path_list = re.split(fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_8(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', )  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_9(self, fname):
        "Set the field name."

        path_list = re.rsplit('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_10(self, fname):
        "Set the field name."

        path_list = re.split('XX[.[]XX', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_11(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = None
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_12(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[1]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_13(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = None
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_14(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = None
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_15(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[2:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_16(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = None

    def xǁBaseFormatFieldǁset_fname__mutmut_17(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name and self.base_name.isdigit()

    def xǁBaseFormatFieldǁset_fname__mutmut_18(self, fname):
        "Set the field name."

        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = self.base_name or self.base_name.isdigit()
    
    xǁBaseFormatFieldǁset_fname__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseFormatFieldǁset_fname__mutmut_1': xǁBaseFormatFieldǁset_fname__mutmut_1, 
        'xǁBaseFormatFieldǁset_fname__mutmut_2': xǁBaseFormatFieldǁset_fname__mutmut_2, 
        'xǁBaseFormatFieldǁset_fname__mutmut_3': xǁBaseFormatFieldǁset_fname__mutmut_3, 
        'xǁBaseFormatFieldǁset_fname__mutmut_4': xǁBaseFormatFieldǁset_fname__mutmut_4, 
        'xǁBaseFormatFieldǁset_fname__mutmut_5': xǁBaseFormatFieldǁset_fname__mutmut_5, 
        'xǁBaseFormatFieldǁset_fname__mutmut_6': xǁBaseFormatFieldǁset_fname__mutmut_6, 
        'xǁBaseFormatFieldǁset_fname__mutmut_7': xǁBaseFormatFieldǁset_fname__mutmut_7, 
        'xǁBaseFormatFieldǁset_fname__mutmut_8': xǁBaseFormatFieldǁset_fname__mutmut_8, 
        'xǁBaseFormatFieldǁset_fname__mutmut_9': xǁBaseFormatFieldǁset_fname__mutmut_9, 
        'xǁBaseFormatFieldǁset_fname__mutmut_10': xǁBaseFormatFieldǁset_fname__mutmut_10, 
        'xǁBaseFormatFieldǁset_fname__mutmut_11': xǁBaseFormatFieldǁset_fname__mutmut_11, 
        'xǁBaseFormatFieldǁset_fname__mutmut_12': xǁBaseFormatFieldǁset_fname__mutmut_12, 
        'xǁBaseFormatFieldǁset_fname__mutmut_13': xǁBaseFormatFieldǁset_fname__mutmut_13, 
        'xǁBaseFormatFieldǁset_fname__mutmut_14': xǁBaseFormatFieldǁset_fname__mutmut_14, 
        'xǁBaseFormatFieldǁset_fname__mutmut_15': xǁBaseFormatFieldǁset_fname__mutmut_15, 
        'xǁBaseFormatFieldǁset_fname__mutmut_16': xǁBaseFormatFieldǁset_fname__mutmut_16, 
        'xǁBaseFormatFieldǁset_fname__mutmut_17': xǁBaseFormatFieldǁset_fname__mutmut_17, 
        'xǁBaseFormatFieldǁset_fname__mutmut_18': xǁBaseFormatFieldǁset_fname__mutmut_18
    }
    
    def set_fname(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseFormatFieldǁset_fname__mutmut_orig"), object.__getattribute__(self, "xǁBaseFormatFieldǁset_fname__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_fname.__signature__ = _mutmut_signature(xǁBaseFormatFieldǁset_fname__mutmut_orig)
    xǁBaseFormatFieldǁset_fname__mutmut_orig.__name__ = 'xǁBaseFormatFieldǁset_fname'

    def xǁBaseFormatFieldǁset_fspec__mutmut_orig(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_1(self, fspec):
        "XXSet the field spec.XX"
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_2(self, fspec):
        "set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_3(self, fspec):
        "SET THE FIELD SPEC."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_4(self, fspec):
        "Set the field spec."
        fspec = None
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_5(self, fspec):
        "Set the field spec."
        fspec = fspec and ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_6(self, fspec):
        "Set the field spec."
        fspec = fspec or 'XXXX'
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_7(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = None
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_8(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(None):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_9(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_10(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(None)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_11(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = None
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_12(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = None
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_13(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = None
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_14(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[+1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_15(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-2:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_16(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = None

    def xǁBaseFormatFieldǁset_fspec__mutmut_17(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(None, str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_18(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, None)

    def xǁBaseFormatFieldǁset_fspec__mutmut_19(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(str)

    def xǁBaseFormatFieldǁset_fspec__mutmut_20(self, fspec):
        "Set the field spec."
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in Formatter().parse(fspec):
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, )
    
    xǁBaseFormatFieldǁset_fspec__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseFormatFieldǁset_fspec__mutmut_1': xǁBaseFormatFieldǁset_fspec__mutmut_1, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_2': xǁBaseFormatFieldǁset_fspec__mutmut_2, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_3': xǁBaseFormatFieldǁset_fspec__mutmut_3, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_4': xǁBaseFormatFieldǁset_fspec__mutmut_4, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_5': xǁBaseFormatFieldǁset_fspec__mutmut_5, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_6': xǁBaseFormatFieldǁset_fspec__mutmut_6, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_7': xǁBaseFormatFieldǁset_fspec__mutmut_7, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_8': xǁBaseFormatFieldǁset_fspec__mutmut_8, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_9': xǁBaseFormatFieldǁset_fspec__mutmut_9, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_10': xǁBaseFormatFieldǁset_fspec__mutmut_10, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_11': xǁBaseFormatFieldǁset_fspec__mutmut_11, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_12': xǁBaseFormatFieldǁset_fspec__mutmut_12, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_13': xǁBaseFormatFieldǁset_fspec__mutmut_13, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_14': xǁBaseFormatFieldǁset_fspec__mutmut_14, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_15': xǁBaseFormatFieldǁset_fspec__mutmut_15, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_16': xǁBaseFormatFieldǁset_fspec__mutmut_16, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_17': xǁBaseFormatFieldǁset_fspec__mutmut_17, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_18': xǁBaseFormatFieldǁset_fspec__mutmut_18, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_19': xǁBaseFormatFieldǁset_fspec__mutmut_19, 
        'xǁBaseFormatFieldǁset_fspec__mutmut_20': xǁBaseFormatFieldǁset_fspec__mutmut_20
    }
    
    def set_fspec(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseFormatFieldǁset_fspec__mutmut_orig"), object.__getattribute__(self, "xǁBaseFormatFieldǁset_fspec__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_fspec.__signature__ = _mutmut_signature(xǁBaseFormatFieldǁset_fspec__mutmut_orig)
    xǁBaseFormatFieldǁset_fspec__mutmut_orig.__name__ = 'xǁBaseFormatFieldǁset_fspec'

    def xǁBaseFormatFieldǁset_conv__mutmut_orig(self, conv):
        """There are only two built-in converters: ``s`` and ``r``. They are
        somewhat rare and appearlike ``"{ref!r}"``."""
        # TODO
        self.conv = conv
        self.conv_func = None  # TODO

    def xǁBaseFormatFieldǁset_conv__mutmut_1(self, conv):
        """There are only two built-in converters: ``s`` and ``r``. They are
        somewhat rare and appearlike ``"{ref!r}"``."""
        # TODO
        self.conv = None
        self.conv_func = None  # TODO

    def xǁBaseFormatFieldǁset_conv__mutmut_2(self, conv):
        """There are only two built-in converters: ``s`` and ``r``. They are
        somewhat rare and appearlike ``"{ref!r}"``."""
        # TODO
        self.conv = conv
        self.conv_func = ""  # TODO
    
    xǁBaseFormatFieldǁset_conv__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseFormatFieldǁset_conv__mutmut_1': xǁBaseFormatFieldǁset_conv__mutmut_1, 
        'xǁBaseFormatFieldǁset_conv__mutmut_2': xǁBaseFormatFieldǁset_conv__mutmut_2
    }
    
    def set_conv(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseFormatFieldǁset_conv__mutmut_orig"), object.__getattribute__(self, "xǁBaseFormatFieldǁset_conv__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_conv.__signature__ = _mutmut_signature(xǁBaseFormatFieldǁset_conv__mutmut_orig)
    xǁBaseFormatFieldǁset_conv__mutmut_orig.__name__ = 'xǁBaseFormatFieldǁset_conv'

    @property
    def fstr(self):
        "The current state of the field in string format."
        return construct_format_field_str(self.fname, self.fspec, self.conv)

    def xǁBaseFormatFieldǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_1(self):
        cn = None
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        args = None
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend(None)
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec == '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != 'XXXX':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_7(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(None)
        args_repr = ', '.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_8(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = None
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_9(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join(None)
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_10(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = 'XX, XX'.join([repr(a) for a in args])
        return f'{cn}({args_repr})'

    def xǁBaseFormatFieldǁ__repr____mutmut_11(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(None) for a in args])
        return f'{cn}({args_repr})'
    
    xǁBaseFormatFieldǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseFormatFieldǁ__repr____mutmut_1': xǁBaseFormatFieldǁ__repr____mutmut_1, 
        'xǁBaseFormatFieldǁ__repr____mutmut_2': xǁBaseFormatFieldǁ__repr____mutmut_2, 
        'xǁBaseFormatFieldǁ__repr____mutmut_3': xǁBaseFormatFieldǁ__repr____mutmut_3, 
        'xǁBaseFormatFieldǁ__repr____mutmut_4': xǁBaseFormatFieldǁ__repr____mutmut_4, 
        'xǁBaseFormatFieldǁ__repr____mutmut_5': xǁBaseFormatFieldǁ__repr____mutmut_5, 
        'xǁBaseFormatFieldǁ__repr____mutmut_6': xǁBaseFormatFieldǁ__repr____mutmut_6, 
        'xǁBaseFormatFieldǁ__repr____mutmut_7': xǁBaseFormatFieldǁ__repr____mutmut_7, 
        'xǁBaseFormatFieldǁ__repr____mutmut_8': xǁBaseFormatFieldǁ__repr____mutmut_8, 
        'xǁBaseFormatFieldǁ__repr____mutmut_9': xǁBaseFormatFieldǁ__repr____mutmut_9, 
        'xǁBaseFormatFieldǁ__repr____mutmut_10': xǁBaseFormatFieldǁ__repr____mutmut_10, 
        'xǁBaseFormatFieldǁ__repr____mutmut_11': xǁBaseFormatFieldǁ__repr____mutmut_11
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseFormatFieldǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁBaseFormatFieldǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁBaseFormatFieldǁ__repr____mutmut_orig)
    xǁBaseFormatFieldǁ__repr____mutmut_orig.__name__ = 'xǁBaseFormatFieldǁ__repr__'

    def __str__(self):
        return self.fstr


_UNSET = object()


class DeferredValue:
    """:class:`DeferredValue` is a wrapper type, used to defer computing
    values which would otherwise be expensive to stringify and
    format. This is most valuable in areas like logging, where one
    would not want to waste time formatting a value for a log message
    which will subsequently be filtered because the message's log
    level was DEBUG and the logger was set to only emit CRITICAL
    messages.

    The :class:``DeferredValue`` is initialized with a callable that
    takes no arguments and returns the value, which can be of any
    type. By default DeferredValue only calls that callable once, and
    future references will get a cached value. This behavior can be
    disabled by setting *cache_value* to ``False``.

    Args:

        func (function): A callable that takes no arguments and
            computes the value being represented.
        cache_value (bool): Whether subsequent usages will call *func*
            again. Defaults to ``True``.

    >>> import sys
    >>> dv = DeferredValue(lambda: len(sys._current_frames()))
    >>> output = "works great in all {0} threads!".format(dv)

    PROTIP: To keep lines shorter, use: ``from formatutils import
    DeferredValue as DV``
    """
    def xǁDeferredValueǁ__init____mutmut_orig(self, func, cache_value=True):
        self.func = func
        self.cache_value = cache_value
        self._value = _UNSET
    def xǁDeferredValueǁ__init____mutmut_1(self, func, cache_value=False):
        self.func = func
        self.cache_value = cache_value
        self._value = _UNSET
    def xǁDeferredValueǁ__init____mutmut_2(self, func, cache_value=True):
        self.func = None
        self.cache_value = cache_value
        self._value = _UNSET
    def xǁDeferredValueǁ__init____mutmut_3(self, func, cache_value=True):
        self.func = func
        self.cache_value = None
        self._value = _UNSET
    def xǁDeferredValueǁ__init____mutmut_4(self, func, cache_value=True):
        self.func = func
        self.cache_value = cache_value
        self._value = None
    
    xǁDeferredValueǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__init____mutmut_1': xǁDeferredValueǁ__init____mutmut_1, 
        'xǁDeferredValueǁ__init____mutmut_2': xǁDeferredValueǁ__init____mutmut_2, 
        'xǁDeferredValueǁ__init____mutmut_3': xǁDeferredValueǁ__init____mutmut_3, 
        'xǁDeferredValueǁ__init____mutmut_4': xǁDeferredValueǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__init____mutmut_orig)
    xǁDeferredValueǁ__init____mutmut_orig.__name__ = 'xǁDeferredValueǁ__init__'

    def xǁDeferredValueǁget_value__mutmut_orig(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET and self.cache_value:
            value = self._value
        else:
            value = self.func()
            if self.cache_value:
                self._value = value
        return value

    def xǁDeferredValueǁget_value__mutmut_1(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET or self.cache_value:
            value = self._value
        else:
            value = self.func()
            if self.cache_value:
                self._value = value
        return value

    def xǁDeferredValueǁget_value__mutmut_2(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is _UNSET and self.cache_value:
            value = self._value
        else:
            value = self.func()
            if self.cache_value:
                self._value = value
        return value

    def xǁDeferredValueǁget_value__mutmut_3(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET and self.cache_value:
            value = None
        else:
            value = self.func()
            if self.cache_value:
                self._value = value
        return value

    def xǁDeferredValueǁget_value__mutmut_4(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET and self.cache_value:
            value = self._value
        else:
            value = None
            if self.cache_value:
                self._value = value
        return value

    def xǁDeferredValueǁget_value__mutmut_5(self):
        """Computes, optionally caches, and returns the value of the
        *func*. If ``get_value()`` has been called before, a cached
        value may be returned depending on the *cache_value* option
        passed to the constructor.
        """
        if self._value is not _UNSET and self.cache_value:
            value = self._value
        else:
            value = self.func()
            if self.cache_value:
                self._value = None
        return value
    
    xǁDeferredValueǁget_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁget_value__mutmut_1': xǁDeferredValueǁget_value__mutmut_1, 
        'xǁDeferredValueǁget_value__mutmut_2': xǁDeferredValueǁget_value__mutmut_2, 
        'xǁDeferredValueǁget_value__mutmut_3': xǁDeferredValueǁget_value__mutmut_3, 
        'xǁDeferredValueǁget_value__mutmut_4': xǁDeferredValueǁget_value__mutmut_4, 
        'xǁDeferredValueǁget_value__mutmut_5': xǁDeferredValueǁget_value__mutmut_5
    }
    
    def get_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁget_value__mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁget_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_value.__signature__ = _mutmut_signature(xǁDeferredValueǁget_value__mutmut_orig)
    xǁDeferredValueǁget_value__mutmut_orig.__name__ = 'xǁDeferredValueǁget_value'

    def xǁDeferredValueǁ__int____mutmut_orig(self):
        return int(self.get_value())

    def xǁDeferredValueǁ__int____mutmut_1(self):
        return int(None)
    
    xǁDeferredValueǁ__int____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__int____mutmut_1': xǁDeferredValueǁ__int____mutmut_1
    }
    
    def __int__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__int____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__int____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __int__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__int____mutmut_orig)
    xǁDeferredValueǁ__int____mutmut_orig.__name__ = 'xǁDeferredValueǁ__int__'

    def xǁDeferredValueǁ__float____mutmut_orig(self):
        return float(self.get_value())

    def xǁDeferredValueǁ__float____mutmut_1(self):
        return float(None)
    
    xǁDeferredValueǁ__float____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__float____mutmut_1': xǁDeferredValueǁ__float____mutmut_1
    }
    
    def __float__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__float____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__float____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __float__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__float____mutmut_orig)
    xǁDeferredValueǁ__float____mutmut_orig.__name__ = 'xǁDeferredValueǁ__float__'

    def xǁDeferredValueǁ__str____mutmut_orig(self):
        return str(self.get_value())

    def xǁDeferredValueǁ__str____mutmut_1(self):
        return str(None)
    
    xǁDeferredValueǁ__str____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__str____mutmut_1': xǁDeferredValueǁ__str____mutmut_1
    }
    
    def __str__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__str____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__str____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __str__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__str____mutmut_orig)
    xǁDeferredValueǁ__str____mutmut_orig.__name__ = 'xǁDeferredValueǁ__str__'

    def xǁDeferredValueǁ__unicode____mutmut_orig(self):
        return str(self.get_value())

    def xǁDeferredValueǁ__unicode____mutmut_1(self):
        return str(None)
    
    xǁDeferredValueǁ__unicode____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__unicode____mutmut_1': xǁDeferredValueǁ__unicode____mutmut_1
    }
    
    def __unicode__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__unicode____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__unicode____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __unicode__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__unicode____mutmut_orig)
    xǁDeferredValueǁ__unicode____mutmut_orig.__name__ = 'xǁDeferredValueǁ__unicode__'

    def xǁDeferredValueǁ__repr____mutmut_orig(self):
        return repr(self.get_value())

    def xǁDeferredValueǁ__repr____mutmut_1(self):
        return repr(None)
    
    xǁDeferredValueǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__repr____mutmut_1': xǁDeferredValueǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__repr____mutmut_orig)
    xǁDeferredValueǁ__repr____mutmut_orig.__name__ = 'xǁDeferredValueǁ__repr__'

    def xǁDeferredValueǁ__format____mutmut_orig(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_1(self, fmt):
        value = None

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_2(self, fmt):
        value = self.get_value()

        pt = None  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_3(self, fmt):
        value = self.get_value()

        pt = fmt[+1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_4(self, fmt):
        value = self.get_value()

        pt = fmt[-2:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_5(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = None

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_6(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(None, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_7(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, None)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_8(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_9(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, )

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_10(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(None)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)

    def xǁDeferredValueǁ__format____mutmut_11(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(None)

    def xǁDeferredValueǁ__format____mutmut_12(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(None).__format__(fmt)
    
    xǁDeferredValueǁ__format____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeferredValueǁ__format____mutmut_1': xǁDeferredValueǁ__format____mutmut_1, 
        'xǁDeferredValueǁ__format____mutmut_2': xǁDeferredValueǁ__format____mutmut_2, 
        'xǁDeferredValueǁ__format____mutmut_3': xǁDeferredValueǁ__format____mutmut_3, 
        'xǁDeferredValueǁ__format____mutmut_4': xǁDeferredValueǁ__format____mutmut_4, 
        'xǁDeferredValueǁ__format____mutmut_5': xǁDeferredValueǁ__format____mutmut_5, 
        'xǁDeferredValueǁ__format____mutmut_6': xǁDeferredValueǁ__format____mutmut_6, 
        'xǁDeferredValueǁ__format____mutmut_7': xǁDeferredValueǁ__format____mutmut_7, 
        'xǁDeferredValueǁ__format____mutmut_8': xǁDeferredValueǁ__format____mutmut_8, 
        'xǁDeferredValueǁ__format____mutmut_9': xǁDeferredValueǁ__format____mutmut_9, 
        'xǁDeferredValueǁ__format____mutmut_10': xǁDeferredValueǁ__format____mutmut_10, 
        'xǁDeferredValueǁ__format____mutmut_11': xǁDeferredValueǁ__format____mutmut_11, 
        'xǁDeferredValueǁ__format____mutmut_12': xǁDeferredValueǁ__format____mutmut_12
    }
    
    def __format__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeferredValueǁ__format____mutmut_orig"), object.__getattribute__(self, "xǁDeferredValueǁ__format____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __format__.__signature__ = _mutmut_signature(xǁDeferredValueǁ__format____mutmut_orig)
    xǁDeferredValueǁ__format____mutmut_orig.__name__ = 'xǁDeferredValueǁ__format__'

# end formatutils.py
