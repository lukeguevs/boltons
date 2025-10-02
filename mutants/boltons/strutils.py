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

"""So much practical programming involves string manipulation, which
Python readily accommodates. Still, there are dozens of basic and
common capabilities missing from the standard library, several of them
provided by ``strutils``.
"""


import builtins
import re
import sys
import uuid
import zlib
import string
import unicodedata
import collections
from collections.abc import Mapping
from gzip import GzipFile
from html.parser import HTMLParser
from html import entities as htmlentitydefs
from io import BytesIO as StringIO


__all__ = ['camel2under', 'under2camel', 'slugify', 'split_punct_ws',
           'unit_len', 'ordinalize', 'cardinalize', 'pluralize', 'singularize',
           'asciify', 'is_ascii', 'is_uuid', 'html2text', 'strip_ansi',
           'bytes2human', 'find_hashtags', 'a10n', 'gzip_bytes', 'gunzip_bytes',
           'iter_splitlines', 'indent', 'escape_shell_args',
           'args2cmd', 'args2sh', 'parse_int_list', 'format_int_list',
           'complement_int_list', 'int_ranges_from_int_list', 'MultiReplace',
           'multi_replace', 'unwrap_text', 'removeprefix']


_punct_ws_str = string.punctuation + string.whitespace
_punct_re = re.compile('[' + _punct_ws_str + ']+')
_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
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


def x_camel2under__mutmut_orig(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()


def x_camel2under__mutmut_1(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).upper()


def x_camel2under__mutmut_2(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(None, camel_string).lower()


def x_camel2under__mutmut_3(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', None).lower()


def x_camel2under__mutmut_4(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(camel_string).lower()


def x_camel2under__mutmut_5(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', ).lower()


def x_camel2under__mutmut_6(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'XX_\1XX', camel_string).lower()


def x_camel2under__mutmut_7(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()


def x_camel2under__mutmut_8(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()

x_camel2under__mutmut_mutants : ClassVar[MutantDict] = {
'x_camel2under__mutmut_1': x_camel2under__mutmut_1, 
    'x_camel2under__mutmut_2': x_camel2under__mutmut_2, 
    'x_camel2under__mutmut_3': x_camel2under__mutmut_3, 
    'x_camel2under__mutmut_4': x_camel2under__mutmut_4, 
    'x_camel2under__mutmut_5': x_camel2under__mutmut_5, 
    'x_camel2under__mutmut_6': x_camel2under__mutmut_6, 
    'x_camel2under__mutmut_7': x_camel2under__mutmut_7, 
    'x_camel2under__mutmut_8': x_camel2under__mutmut_8
}

def camel2under(*args, **kwargs):
    result = _mutmut_trampoline(x_camel2under__mutmut_orig, x_camel2under__mutmut_mutants, args, kwargs)
    return result 

camel2under.__signature__ = _mutmut_signature(x_camel2under__mutmut_orig)
x_camel2under__mutmut_orig.__name__ = 'x_camel2under'


def x_under2camel__mutmut_orig(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split('_'))


def x_under2camel__mutmut_1(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(None)


def x_under2camel__mutmut_2(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return 'XXXX'.join(w.capitalize() or '_' for w in under_string.split('_'))


def x_under2camel__mutmut_3(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() and '_' for w in under_string.split('_'))


def x_under2camel__mutmut_4(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or 'XX_XX' for w in under_string.split('_'))


def x_under2camel__mutmut_5(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split(None))


def x_under2camel__mutmut_6(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split('XX_XX'))

x_under2camel__mutmut_mutants : ClassVar[MutantDict] = {
'x_under2camel__mutmut_1': x_under2camel__mutmut_1, 
    'x_under2camel__mutmut_2': x_under2camel__mutmut_2, 
    'x_under2camel__mutmut_3': x_under2camel__mutmut_3, 
    'x_under2camel__mutmut_4': x_under2camel__mutmut_4, 
    'x_under2camel__mutmut_5': x_under2camel__mutmut_5, 
    'x_under2camel__mutmut_6': x_under2camel__mutmut_6
}

def under2camel(*args, **kwargs):
    result = _mutmut_trampoline(x_under2camel__mutmut_orig, x_under2camel__mutmut_mutants, args, kwargs)
    return result 

under2camel.__signature__ = _mutmut_signature(x_under2camel__mutmut_orig)
x_under2camel__mutmut_orig.__name__ = 'x_under2camel'


def x_slugify__mutmut_orig(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_1(text, delim='XX_XX', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_2(text, delim='_', lower=False, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_3(text, delim='_', lower=True, ascii=True):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_4(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = None
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_5(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) and delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_6(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(None) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_7(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(None)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_8(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else 'XXXX'
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_9(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = None
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_10(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(None)
    if lower:
        ret = ret.lower()
    return ret


def x_slugify__mutmut_11(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = None
    return ret


def x_slugify__mutmut_12(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.upper()
    return ret

x_slugify__mutmut_mutants : ClassVar[MutantDict] = {
'x_slugify__mutmut_1': x_slugify__mutmut_1, 
    'x_slugify__mutmut_2': x_slugify__mutmut_2, 
    'x_slugify__mutmut_3': x_slugify__mutmut_3, 
    'x_slugify__mutmut_4': x_slugify__mutmut_4, 
    'x_slugify__mutmut_5': x_slugify__mutmut_5, 
    'x_slugify__mutmut_6': x_slugify__mutmut_6, 
    'x_slugify__mutmut_7': x_slugify__mutmut_7, 
    'x_slugify__mutmut_8': x_slugify__mutmut_8, 
    'x_slugify__mutmut_9': x_slugify__mutmut_9, 
    'x_slugify__mutmut_10': x_slugify__mutmut_10, 
    'x_slugify__mutmut_11': x_slugify__mutmut_11, 
    'x_slugify__mutmut_12': x_slugify__mutmut_12
}

def slugify(*args, **kwargs):
    result = _mutmut_trampoline(x_slugify__mutmut_orig, x_slugify__mutmut_mutants, args, kwargs)
    return result 

slugify.__signature__ = _mutmut_signature(x_slugify__mutmut_orig)
x_slugify__mutmut_orig.__name__ = 'x_slugify'


def x_split_punct_ws__mutmut_orig(text):
    """While :meth:`str.split` will split on whitespace,
    :func:`split_punct_ws` will split on punctuation and
    whitespace. This used internally by :func:`slugify`, above.

    >>> split_punct_ws('First post! Hi!!!!~1    ')
    ['First', 'post', 'Hi', '1']
    """
    return [w for w in _punct_re.split(text) if w]


def x_split_punct_ws__mutmut_1(text):
    """While :meth:`str.split` will split on whitespace,
    :func:`split_punct_ws` will split on punctuation and
    whitespace. This used internally by :func:`slugify`, above.

    >>> split_punct_ws('First post! Hi!!!!~1    ')
    ['First', 'post', 'Hi', '1']
    """
    return [w for w in _punct_re.split(None) if w]

x_split_punct_ws__mutmut_mutants : ClassVar[MutantDict] = {
'x_split_punct_ws__mutmut_1': x_split_punct_ws__mutmut_1
}

def split_punct_ws(*args, **kwargs):
    result = _mutmut_trampoline(x_split_punct_ws__mutmut_orig, x_split_punct_ws__mutmut_mutants, args, kwargs)
    return result 

split_punct_ws.__signature__ = _mutmut_signature(x_split_punct_ws__mutmut_orig)
x_split_punct_ws__mutmut_orig.__name__ = 'x_split_punct_ws'


def x_unit_len__mutmut_orig(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_1(sized_iterable, unit_noun='XXitemXX'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_2(sized_iterable, unit_noun='ITEM'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_3(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = None
    units = cardinalize(unit_noun, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_4(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = None
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_5(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(None, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_6(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, None)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_7(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


def x_unit_len__mutmut_8(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, )
    if count:
        return f'{count} {units}'
    return f'No {units}'

x_unit_len__mutmut_mutants : ClassVar[MutantDict] = {
'x_unit_len__mutmut_1': x_unit_len__mutmut_1, 
    'x_unit_len__mutmut_2': x_unit_len__mutmut_2, 
    'x_unit_len__mutmut_3': x_unit_len__mutmut_3, 
    'x_unit_len__mutmut_4': x_unit_len__mutmut_4, 
    'x_unit_len__mutmut_5': x_unit_len__mutmut_5, 
    'x_unit_len__mutmut_6': x_unit_len__mutmut_6, 
    'x_unit_len__mutmut_7': x_unit_len__mutmut_7, 
    'x_unit_len__mutmut_8': x_unit_len__mutmut_8
}

def unit_len(*args, **kwargs):
    result = _mutmut_trampoline(x_unit_len__mutmut_orig, x_unit_len__mutmut_mutants, args, kwargs)
    return result 

unit_len.__signature__ = _mutmut_signature(x_unit_len__mutmut_orig)
x_unit_len__mutmut_orig.__name__ = 'x_unit_len'


_ORDINAL_MAP = {'1': 'st',
                '2': 'nd',
                '3': 'rd'}  # 'th' is the default


def x_ordinalize__mutmut_orig(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_1(number, ext_only=True):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_2(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = None
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_3(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(None), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_4(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), 'XXXX'
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_5(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr or numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_6(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[+1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_7(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-2] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_8(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] not in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_9(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[+2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_10(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-3] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_11(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] != '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_12(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == 'XX1XX':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_13(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = None
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_14(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'XXthXX'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_15(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'TH'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_16(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = None
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_17(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(None, 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_18(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], None)
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_19(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get('th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_20(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], )
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_21(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[+1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_22(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-2], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_23(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'XXthXX')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_24(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'TH')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_25(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = None
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_26(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(None, 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_27(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], None)
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_28(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get('th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_29(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], )
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_30(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[+1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_31(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-2], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_32(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'XXthXX')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_33(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'TH')
    if ext_only:
        return ext
    else:
        return numstr + ext


def x_ordinalize__mutmut_34(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr - ext

x_ordinalize__mutmut_mutants : ClassVar[MutantDict] = {
'x_ordinalize__mutmut_1': x_ordinalize__mutmut_1, 
    'x_ordinalize__mutmut_2': x_ordinalize__mutmut_2, 
    'x_ordinalize__mutmut_3': x_ordinalize__mutmut_3, 
    'x_ordinalize__mutmut_4': x_ordinalize__mutmut_4, 
    'x_ordinalize__mutmut_5': x_ordinalize__mutmut_5, 
    'x_ordinalize__mutmut_6': x_ordinalize__mutmut_6, 
    'x_ordinalize__mutmut_7': x_ordinalize__mutmut_7, 
    'x_ordinalize__mutmut_8': x_ordinalize__mutmut_8, 
    'x_ordinalize__mutmut_9': x_ordinalize__mutmut_9, 
    'x_ordinalize__mutmut_10': x_ordinalize__mutmut_10, 
    'x_ordinalize__mutmut_11': x_ordinalize__mutmut_11, 
    'x_ordinalize__mutmut_12': x_ordinalize__mutmut_12, 
    'x_ordinalize__mutmut_13': x_ordinalize__mutmut_13, 
    'x_ordinalize__mutmut_14': x_ordinalize__mutmut_14, 
    'x_ordinalize__mutmut_15': x_ordinalize__mutmut_15, 
    'x_ordinalize__mutmut_16': x_ordinalize__mutmut_16, 
    'x_ordinalize__mutmut_17': x_ordinalize__mutmut_17, 
    'x_ordinalize__mutmut_18': x_ordinalize__mutmut_18, 
    'x_ordinalize__mutmut_19': x_ordinalize__mutmut_19, 
    'x_ordinalize__mutmut_20': x_ordinalize__mutmut_20, 
    'x_ordinalize__mutmut_21': x_ordinalize__mutmut_21, 
    'x_ordinalize__mutmut_22': x_ordinalize__mutmut_22, 
    'x_ordinalize__mutmut_23': x_ordinalize__mutmut_23, 
    'x_ordinalize__mutmut_24': x_ordinalize__mutmut_24, 
    'x_ordinalize__mutmut_25': x_ordinalize__mutmut_25, 
    'x_ordinalize__mutmut_26': x_ordinalize__mutmut_26, 
    'x_ordinalize__mutmut_27': x_ordinalize__mutmut_27, 
    'x_ordinalize__mutmut_28': x_ordinalize__mutmut_28, 
    'x_ordinalize__mutmut_29': x_ordinalize__mutmut_29, 
    'x_ordinalize__mutmut_30': x_ordinalize__mutmut_30, 
    'x_ordinalize__mutmut_31': x_ordinalize__mutmut_31, 
    'x_ordinalize__mutmut_32': x_ordinalize__mutmut_32, 
    'x_ordinalize__mutmut_33': x_ordinalize__mutmut_33, 
    'x_ordinalize__mutmut_34': x_ordinalize__mutmut_34
}

def ordinalize(*args, **kwargs):
    result = _mutmut_trampoline(x_ordinalize__mutmut_orig, x_ordinalize__mutmut_mutants, args, kwargs)
    return result 

ordinalize.__signature__ = _mutmut_signature(x_ordinalize__mutmut_orig)
x_ordinalize__mutmut_orig.__name__ = 'x_ordinalize'


def x_cardinalize__mutmut_orig(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count == 1:
        return unit_noun
    return pluralize(unit_noun)


def x_cardinalize__mutmut_1(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count != 1:
        return unit_noun
    return pluralize(unit_noun)


def x_cardinalize__mutmut_2(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count == 2:
        return unit_noun
    return pluralize(unit_noun)


def x_cardinalize__mutmut_3(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count == 1:
        return unit_noun
    return pluralize(None)

x_cardinalize__mutmut_mutants : ClassVar[MutantDict] = {
'x_cardinalize__mutmut_1': x_cardinalize__mutmut_1, 
    'x_cardinalize__mutmut_2': x_cardinalize__mutmut_2, 
    'x_cardinalize__mutmut_3': x_cardinalize__mutmut_3
}

def cardinalize(*args, **kwargs):
    result = _mutmut_trampoline(x_cardinalize__mutmut_orig, x_cardinalize__mutmut_mutants, args, kwargs)
    return result 

cardinalize.__signature__ = _mutmut_signature(x_cardinalize__mutmut_orig)
x_cardinalize__mutmut_orig.__name__ = 'x_cardinalize'


def x_singularize__mutmut_orig(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_1(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = None
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_2(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().upper()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_3(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word and word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_4(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_5(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word not in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_6(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = None
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_7(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(None)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_8(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = None
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_9(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_10(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith(None):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_11(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('XXsXX'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_12(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('S'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_13(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) != 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_14(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 3:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_15(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = None  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_16(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:+1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_17(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-2]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_18(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') or word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_19(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith(None) and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_20(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('XXiesXX') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_21(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('IES') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_22(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[+4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_23(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-5:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_24(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:+3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_25(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-4] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_26(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_27(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'XXaeiouXX':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_28(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'AEIOU':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_29(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = None
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_30(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] - 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_31(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:+3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_32(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-4] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_33(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'XXyXX'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_34(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'Y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_35(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') or word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_36(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith(None) and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_37(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('XXesXX') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_38(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('ES') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_39(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[+3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_40(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-4] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_41(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] != 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_42(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 'XXsXX':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_43(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 'S':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_44(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = None
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_45(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:+2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_46(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-3]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_47(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = None
    return _match_case(orig_word, singular)


def x_singularize__mutmut_48(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:+1]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_49(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-2]
    return _match_case(orig_word, singular)


def x_singularize__mutmut_50(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(None, singular)


def x_singularize__mutmut_51(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, None)


def x_singularize__mutmut_52(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(singular)


def x_singularize__mutmut_53(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, )

x_singularize__mutmut_mutants : ClassVar[MutantDict] = {
'x_singularize__mutmut_1': x_singularize__mutmut_1, 
    'x_singularize__mutmut_2': x_singularize__mutmut_2, 
    'x_singularize__mutmut_3': x_singularize__mutmut_3, 
    'x_singularize__mutmut_4': x_singularize__mutmut_4, 
    'x_singularize__mutmut_5': x_singularize__mutmut_5, 
    'x_singularize__mutmut_6': x_singularize__mutmut_6, 
    'x_singularize__mutmut_7': x_singularize__mutmut_7, 
    'x_singularize__mutmut_8': x_singularize__mutmut_8, 
    'x_singularize__mutmut_9': x_singularize__mutmut_9, 
    'x_singularize__mutmut_10': x_singularize__mutmut_10, 
    'x_singularize__mutmut_11': x_singularize__mutmut_11, 
    'x_singularize__mutmut_12': x_singularize__mutmut_12, 
    'x_singularize__mutmut_13': x_singularize__mutmut_13, 
    'x_singularize__mutmut_14': x_singularize__mutmut_14, 
    'x_singularize__mutmut_15': x_singularize__mutmut_15, 
    'x_singularize__mutmut_16': x_singularize__mutmut_16, 
    'x_singularize__mutmut_17': x_singularize__mutmut_17, 
    'x_singularize__mutmut_18': x_singularize__mutmut_18, 
    'x_singularize__mutmut_19': x_singularize__mutmut_19, 
    'x_singularize__mutmut_20': x_singularize__mutmut_20, 
    'x_singularize__mutmut_21': x_singularize__mutmut_21, 
    'x_singularize__mutmut_22': x_singularize__mutmut_22, 
    'x_singularize__mutmut_23': x_singularize__mutmut_23, 
    'x_singularize__mutmut_24': x_singularize__mutmut_24, 
    'x_singularize__mutmut_25': x_singularize__mutmut_25, 
    'x_singularize__mutmut_26': x_singularize__mutmut_26, 
    'x_singularize__mutmut_27': x_singularize__mutmut_27, 
    'x_singularize__mutmut_28': x_singularize__mutmut_28, 
    'x_singularize__mutmut_29': x_singularize__mutmut_29, 
    'x_singularize__mutmut_30': x_singularize__mutmut_30, 
    'x_singularize__mutmut_31': x_singularize__mutmut_31, 
    'x_singularize__mutmut_32': x_singularize__mutmut_32, 
    'x_singularize__mutmut_33': x_singularize__mutmut_33, 
    'x_singularize__mutmut_34': x_singularize__mutmut_34, 
    'x_singularize__mutmut_35': x_singularize__mutmut_35, 
    'x_singularize__mutmut_36': x_singularize__mutmut_36, 
    'x_singularize__mutmut_37': x_singularize__mutmut_37, 
    'x_singularize__mutmut_38': x_singularize__mutmut_38, 
    'x_singularize__mutmut_39': x_singularize__mutmut_39, 
    'x_singularize__mutmut_40': x_singularize__mutmut_40, 
    'x_singularize__mutmut_41': x_singularize__mutmut_41, 
    'x_singularize__mutmut_42': x_singularize__mutmut_42, 
    'x_singularize__mutmut_43': x_singularize__mutmut_43, 
    'x_singularize__mutmut_44': x_singularize__mutmut_44, 
    'x_singularize__mutmut_45': x_singularize__mutmut_45, 
    'x_singularize__mutmut_46': x_singularize__mutmut_46, 
    'x_singularize__mutmut_47': x_singularize__mutmut_47, 
    'x_singularize__mutmut_48': x_singularize__mutmut_48, 
    'x_singularize__mutmut_49': x_singularize__mutmut_49, 
    'x_singularize__mutmut_50': x_singularize__mutmut_50, 
    'x_singularize__mutmut_51': x_singularize__mutmut_51, 
    'x_singularize__mutmut_52': x_singularize__mutmut_52, 
    'x_singularize__mutmut_53': x_singularize__mutmut_53
}

def singularize(*args, **kwargs):
    result = _mutmut_trampoline(x_singularize__mutmut_orig, x_singularize__mutmut_mutants, args, kwargs)
    return result 

singularize.__signature__ = _mutmut_signature(x_singularize__mutmut_orig)
x_singularize__mutmut_orig.__name__ = 'x_singularize'


def x_pluralize__mutmut_orig(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_1(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = None
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_2(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().upper()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_3(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word and word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_4(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_5(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word not in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_6(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = None
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_7(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(None)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_8(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = None
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_9(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') or word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_10(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith(None) and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_11(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('XXyXX') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_12(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('Y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_13(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[+2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_14(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-3:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_15(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:+1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_16(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-2] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_17(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_18(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'XXaeiouXX':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_19(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'AEIOU':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_20(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = None
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_21(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] - 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_22(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:+1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_23(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-2] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_24(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'XXiesXX'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_25(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'IES'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_26(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') and word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_27(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' and word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_28(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[+1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_29(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-2] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_30(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] != 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_31(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 'XXsXX' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_32(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 'S' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_33(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith(None) or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_34(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('XXchXX') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_35(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('CH') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_36(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith(None):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_37(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('XXshXX'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_38(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('SH'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_39(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = None
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_40(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith(None) else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_41(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('XXesXX') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_42(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('ES') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_43(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word - 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_44(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'XXesXX'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_45(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'ES'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_46(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = None
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_47(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word - 's'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_48(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 'XXsXX'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_49(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 'S'
    return _match_case(orig_word, plural)


def x_pluralize__mutmut_50(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(None, plural)


def x_pluralize__mutmut_51(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, None)


def x_pluralize__mutmut_52(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(plural)


def x_pluralize__mutmut_53(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, )

x_pluralize__mutmut_mutants : ClassVar[MutantDict] = {
'x_pluralize__mutmut_1': x_pluralize__mutmut_1, 
    'x_pluralize__mutmut_2': x_pluralize__mutmut_2, 
    'x_pluralize__mutmut_3': x_pluralize__mutmut_3, 
    'x_pluralize__mutmut_4': x_pluralize__mutmut_4, 
    'x_pluralize__mutmut_5': x_pluralize__mutmut_5, 
    'x_pluralize__mutmut_6': x_pluralize__mutmut_6, 
    'x_pluralize__mutmut_7': x_pluralize__mutmut_7, 
    'x_pluralize__mutmut_8': x_pluralize__mutmut_8, 
    'x_pluralize__mutmut_9': x_pluralize__mutmut_9, 
    'x_pluralize__mutmut_10': x_pluralize__mutmut_10, 
    'x_pluralize__mutmut_11': x_pluralize__mutmut_11, 
    'x_pluralize__mutmut_12': x_pluralize__mutmut_12, 
    'x_pluralize__mutmut_13': x_pluralize__mutmut_13, 
    'x_pluralize__mutmut_14': x_pluralize__mutmut_14, 
    'x_pluralize__mutmut_15': x_pluralize__mutmut_15, 
    'x_pluralize__mutmut_16': x_pluralize__mutmut_16, 
    'x_pluralize__mutmut_17': x_pluralize__mutmut_17, 
    'x_pluralize__mutmut_18': x_pluralize__mutmut_18, 
    'x_pluralize__mutmut_19': x_pluralize__mutmut_19, 
    'x_pluralize__mutmut_20': x_pluralize__mutmut_20, 
    'x_pluralize__mutmut_21': x_pluralize__mutmut_21, 
    'x_pluralize__mutmut_22': x_pluralize__mutmut_22, 
    'x_pluralize__mutmut_23': x_pluralize__mutmut_23, 
    'x_pluralize__mutmut_24': x_pluralize__mutmut_24, 
    'x_pluralize__mutmut_25': x_pluralize__mutmut_25, 
    'x_pluralize__mutmut_26': x_pluralize__mutmut_26, 
    'x_pluralize__mutmut_27': x_pluralize__mutmut_27, 
    'x_pluralize__mutmut_28': x_pluralize__mutmut_28, 
    'x_pluralize__mutmut_29': x_pluralize__mutmut_29, 
    'x_pluralize__mutmut_30': x_pluralize__mutmut_30, 
    'x_pluralize__mutmut_31': x_pluralize__mutmut_31, 
    'x_pluralize__mutmut_32': x_pluralize__mutmut_32, 
    'x_pluralize__mutmut_33': x_pluralize__mutmut_33, 
    'x_pluralize__mutmut_34': x_pluralize__mutmut_34, 
    'x_pluralize__mutmut_35': x_pluralize__mutmut_35, 
    'x_pluralize__mutmut_36': x_pluralize__mutmut_36, 
    'x_pluralize__mutmut_37': x_pluralize__mutmut_37, 
    'x_pluralize__mutmut_38': x_pluralize__mutmut_38, 
    'x_pluralize__mutmut_39': x_pluralize__mutmut_39, 
    'x_pluralize__mutmut_40': x_pluralize__mutmut_40, 
    'x_pluralize__mutmut_41': x_pluralize__mutmut_41, 
    'x_pluralize__mutmut_42': x_pluralize__mutmut_42, 
    'x_pluralize__mutmut_43': x_pluralize__mutmut_43, 
    'x_pluralize__mutmut_44': x_pluralize__mutmut_44, 
    'x_pluralize__mutmut_45': x_pluralize__mutmut_45, 
    'x_pluralize__mutmut_46': x_pluralize__mutmut_46, 
    'x_pluralize__mutmut_47': x_pluralize__mutmut_47, 
    'x_pluralize__mutmut_48': x_pluralize__mutmut_48, 
    'x_pluralize__mutmut_49': x_pluralize__mutmut_49, 
    'x_pluralize__mutmut_50': x_pluralize__mutmut_50, 
    'x_pluralize__mutmut_51': x_pluralize__mutmut_51, 
    'x_pluralize__mutmut_52': x_pluralize__mutmut_52, 
    'x_pluralize__mutmut_53': x_pluralize__mutmut_53
}

def pluralize(*args, **kwargs):
    result = _mutmut_trampoline(x_pluralize__mutmut_orig, x_pluralize__mutmut_mutants, args, kwargs)
    return result 

pluralize.__signature__ = _mutmut_signature(x_pluralize__mutmut_orig)
x_pluralize__mutmut_orig.__name__ = 'x_pluralize'


def x__match_case__mutmut_orig(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_1(master, disciple):
    if master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_2(master, disciple):
    if not master.strip():
        return disciple
    if master.upper() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_3(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() != master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_4(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.upper()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_5(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.lower() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_6(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() != master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_7(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.lower()
    elif master.title() == master:
        return disciple.title()
    return disciple


def x__match_case__mutmut_8(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() != master:
        return disciple.title()
    return disciple

x__match_case__mutmut_mutants : ClassVar[MutantDict] = {
'x__match_case__mutmut_1': x__match_case__mutmut_1, 
    'x__match_case__mutmut_2': x__match_case__mutmut_2, 
    'x__match_case__mutmut_3': x__match_case__mutmut_3, 
    'x__match_case__mutmut_4': x__match_case__mutmut_4, 
    'x__match_case__mutmut_5': x__match_case__mutmut_5, 
    'x__match_case__mutmut_6': x__match_case__mutmut_6, 
    'x__match_case__mutmut_7': x__match_case__mutmut_7, 
    'x__match_case__mutmut_8': x__match_case__mutmut_8
}

def _match_case(*args, **kwargs):
    result = _mutmut_trampoline(x__match_case__mutmut_orig, x__match_case__mutmut_mutants, args, kwargs)
    return result 

_match_case.__signature__ = _mutmut_signature(x__match_case__mutmut_orig)
x__match_case__mutmut_orig.__name__ = 'x__match_case'


# Singular to plural map of irregular pluralizations
_IRR_S2P = {'addendum': 'addenda', 'alga': 'algae', 'alumna': 'alumnae',
            'alumnus': 'alumni', 'analysis': 'analyses', 'antenna': 'antennae',
            'appendix': 'appendices', 'axis': 'axes', 'bacillus': 'bacilli',
            'bacterium': 'bacteria', 'basis': 'bases', 'beau': 'beaux',
            'bison': 'bison', 'bureau': 'bureaus', 'cactus': 'cacti',
            'calf': 'calves', 'child': 'children', 'corps': 'corps',
            'corpus': 'corpora', 'crisis': 'crises', 'criterion': 'criteria',
            'curriculum': 'curricula', 'datum': 'data', 'deer': 'deer',
            'diagnosis': 'diagnoses', 'die': 'dice', 'dwarf': 'dwarves',
            'echo': 'echoes', 'elf': 'elves', 'ellipsis': 'ellipses',
            'embargo': 'embargoes', 'emphasis': 'emphases', 'erratum': 'errata',
            'fireman': 'firemen', 'fish': 'fish', 'focus': 'foci',
            'foot': 'feet', 'formula': 'formulae', 'formula': 'formulas',
            'fungus': 'fungi', 'genus': 'genera', 'goose': 'geese',
            'half': 'halves', 'hero': 'heroes', 'hippopotamus': 'hippopotami',
            'hoof': 'hooves', 'hypothesis': 'hypotheses', 'index': 'indices',
            'knife': 'knives', 'leaf': 'leaves', 'life': 'lives',
            'loaf': 'loaves', 'louse': 'lice', 'man': 'men',
            'matrix': 'matrices', 'means': 'means', 'medium': 'media',
            'memorandum': 'memoranda', 'millennium': 'milennia', 'moose': 'moose',
            'mosquito': 'mosquitoes', 'mouse': 'mice', 'nebula': 'nebulae',
            'neurosis': 'neuroses', 'nucleus': 'nuclei', 'oasis': 'oases',
            'octopus': 'octopi', 'offspring': 'offspring', 'ovum': 'ova',
            'ox': 'oxen', 'paralysis': 'paralyses', 'parenthesis': 'parentheses',
            'person': 'people', 'phenomenon': 'phenomena', 'potato': 'potatoes',
            'radius': 'radii', 'scarf': 'scarves', 'scissors': 'scissors',
            'self': 'selves', 'sense': 'senses', 'series': 'series', 'sheep':
            'sheep', 'shelf': 'shelves', 'species': 'species', 'stimulus':
            'stimuli', 'stratum': 'strata', 'syllabus': 'syllabi', 'symposium':
            'symposia', 'synopsis': 'synopses', 'synthesis': 'syntheses',
            'tableau': 'tableaux', 'that': 'those', 'thesis': 'theses',
            'thief': 'thieves', 'this': 'these', 'tomato': 'tomatoes', 'tooth':
            'teeth', 'torpedo': 'torpedoes', 'vertebra': 'vertebrae', 'veto':
            'vetoes', 'vita': 'vitae', 'watch': 'watches', 'wife': 'wives',
            'wolf': 'wolves', 'woman': 'women'}


# Reverse index of the above
_IRR_P2S = {v: k for k, v in _IRR_S2P.items()}

HASHTAG_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)", re.UNICODE)


def x_find_hashtags__mutmut_orig(string):
    """Finds and returns all hashtags in a string, with the hashmark
    removed. Supports full-width hashmarks for Asian languages and
    does not false-positive on URL anchors.

    >>> find_hashtags('#atag http://asite/#ananchor')
    ['atag']

    ``find_hashtags`` also works with unicode hashtags.
    """

    # the following works, doctest just struggles with it
    # >>> find_hashtags(u"can't get enough of that dignity chicken #肯德基 woo")
    # [u'\u80af\u5fb7\u57fa']
    return HASHTAG_RE.findall(string)


def x_find_hashtags__mutmut_1(string):
    """Finds and returns all hashtags in a string, with the hashmark
    removed. Supports full-width hashmarks for Asian languages and
    does not false-positive on URL anchors.

    >>> find_hashtags('#atag http://asite/#ananchor')
    ['atag']

    ``find_hashtags`` also works with unicode hashtags.
    """

    # the following works, doctest just struggles with it
    # >>> find_hashtags(u"can't get enough of that dignity chicken #肯德基 woo")
    # [u'\u80af\u5fb7\u57fa']
    return HASHTAG_RE.findall(None)

x_find_hashtags__mutmut_mutants : ClassVar[MutantDict] = {
'x_find_hashtags__mutmut_1': x_find_hashtags__mutmut_1
}

def find_hashtags(*args, **kwargs):
    result = _mutmut_trampoline(x_find_hashtags__mutmut_orig, x_find_hashtags__mutmut_mutants, args, kwargs)
    return result 

find_hashtags.__signature__ = _mutmut_signature(x_find_hashtags__mutmut_orig)
x_find_hashtags__mutmut_orig.__name__ = 'x_find_hashtags'


def x_a10n__mutmut_orig(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[-1]}'


def x_a10n__mutmut_1(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) <= 3:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[-1]}'


def x_a10n__mutmut_2(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 4:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[-1]}'


def x_a10n__mutmut_3(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return f'{string[1]}{len(string[1:-1])}{string[-1]}'


def x_a10n__mutmut_4(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[+1]}'


def x_a10n__mutmut_5(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[-2]}'

x_a10n__mutmut_mutants : ClassVar[MutantDict] = {
'x_a10n__mutmut_1': x_a10n__mutmut_1, 
    'x_a10n__mutmut_2': x_a10n__mutmut_2, 
    'x_a10n__mutmut_3': x_a10n__mutmut_3, 
    'x_a10n__mutmut_4': x_a10n__mutmut_4, 
    'x_a10n__mutmut_5': x_a10n__mutmut_5
}

def a10n(*args, **kwargs):
    result = _mutmut_trampoline(x_a10n__mutmut_orig, x_a10n__mutmut_mutants, args, kwargs)
    return result 

a10n.__signature__ = _mutmut_signature(x_a10n__mutmut_orig)
x_a10n__mutmut_orig.__name__ = 'x_a10n'


# Based on https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences
ANSI_SEQUENCES = re.compile(r'''
    \x1B            # Sequence starts with ESC, i.e. hex 0x1B
    (?:
        [@-Z\\-_]   # Second byte:
                    #   all 0x40–0x5F range but CSI char, i.e ASCII @A–Z\]^_
    |               # Or
        \[          # CSI sequences, starting with [
        [0-?]*      # Parameter bytes:
                    #   range 0x30–0x3F, ASCII 0–9:;<=>?
        [ -/]*      # Intermediate bytes:
                    #   range 0x20–0x2F, ASCII space and !"#$%&'()*+,-./
        [@-~]       # Final byte
                    #   range 0x40–0x7E, ASCII @A–Z[\]^_`a–z{|}~
    )
''', re.VERBOSE)


def x_strip_ansi__mutmut_orig(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_1(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = ""
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_2(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = None
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_3(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(None)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_4(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = None

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_5(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode(None)

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_6(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('XXutf-8XX')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_7(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('UTF-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_8(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = None

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_9(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub(None, text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_10(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', None)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_11(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub(text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_12(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', )

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_13(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('XXXX', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_14(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type or target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_15(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type == type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_16(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(None):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_17(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = None

    return cleaned


def x_strip_ansi__mutmut_18(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(None, 'utf-8')

    return cleaned


def x_strip_ansi__mutmut_19(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, None)

    return cleaned


def x_strip_ansi__mutmut_20(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type('utf-8')

    return cleaned


def x_strip_ansi__mutmut_21(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, )

    return cleaned


def x_strip_ansi__mutmut_22(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'XXutf-8XX')

    return cleaned


def x_strip_ansi__mutmut_23(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'UTF-8')

    return cleaned

x_strip_ansi__mutmut_mutants : ClassVar[MutantDict] = {
'x_strip_ansi__mutmut_1': x_strip_ansi__mutmut_1, 
    'x_strip_ansi__mutmut_2': x_strip_ansi__mutmut_2, 
    'x_strip_ansi__mutmut_3': x_strip_ansi__mutmut_3, 
    'x_strip_ansi__mutmut_4': x_strip_ansi__mutmut_4, 
    'x_strip_ansi__mutmut_5': x_strip_ansi__mutmut_5, 
    'x_strip_ansi__mutmut_6': x_strip_ansi__mutmut_6, 
    'x_strip_ansi__mutmut_7': x_strip_ansi__mutmut_7, 
    'x_strip_ansi__mutmut_8': x_strip_ansi__mutmut_8, 
    'x_strip_ansi__mutmut_9': x_strip_ansi__mutmut_9, 
    'x_strip_ansi__mutmut_10': x_strip_ansi__mutmut_10, 
    'x_strip_ansi__mutmut_11': x_strip_ansi__mutmut_11, 
    'x_strip_ansi__mutmut_12': x_strip_ansi__mutmut_12, 
    'x_strip_ansi__mutmut_13': x_strip_ansi__mutmut_13, 
    'x_strip_ansi__mutmut_14': x_strip_ansi__mutmut_14, 
    'x_strip_ansi__mutmut_15': x_strip_ansi__mutmut_15, 
    'x_strip_ansi__mutmut_16': x_strip_ansi__mutmut_16, 
    'x_strip_ansi__mutmut_17': x_strip_ansi__mutmut_17, 
    'x_strip_ansi__mutmut_18': x_strip_ansi__mutmut_18, 
    'x_strip_ansi__mutmut_19': x_strip_ansi__mutmut_19, 
    'x_strip_ansi__mutmut_20': x_strip_ansi__mutmut_20, 
    'x_strip_ansi__mutmut_21': x_strip_ansi__mutmut_21, 
    'x_strip_ansi__mutmut_22': x_strip_ansi__mutmut_22, 
    'x_strip_ansi__mutmut_23': x_strip_ansi__mutmut_23
}

def strip_ansi(*args, **kwargs):
    result = _mutmut_trampoline(x_strip_ansi__mutmut_orig, x_strip_ansi__mutmut_mutants, args, kwargs)
    return result 

strip_ansi.__signature__ = _mutmut_signature(x_strip_ansi__mutmut_orig)
x_strip_ansi__mutmut_orig.__name__ = 'x_strip_ansi'


def x_asciify__mutmut_orig(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_1(text, ignore=True):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_2(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode(None)
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_3(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('XXasciiXX')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_4(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ASCII')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_5(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = None
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_6(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode(None)
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_7(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('XXutf-8XX')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_8(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('UTF-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_9(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode(None)
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_10(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('XXasciiXX')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_11(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ASCII')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_12(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = None
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_13(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'XXreplaceXX'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_14(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'REPLACE'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_15(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = None
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_16(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'XXignoreXX'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_17(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'IGNORE'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_18(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = None
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_19(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize(None, text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_20(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', None)
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_21(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize(text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_22(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', )
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_23(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('XXNFKDXX', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_24(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('nfkd', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_25(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(None))
        ret = transd.encode('ascii', mode)
        return ret


def x_asciify__mutmut_26(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = None
        return ret


def x_asciify__mutmut_27(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode(None, mode)
        return ret


def x_asciify__mutmut_28(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', None)
        return ret


def x_asciify__mutmut_29(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode(mode)
        return ret


def x_asciify__mutmut_30(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', )
        return ret


def x_asciify__mutmut_31(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('XXasciiXX', mode)
        return ret


def x_asciify__mutmut_32(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ASCII', mode)
        return ret

x_asciify__mutmut_mutants : ClassVar[MutantDict] = {
'x_asciify__mutmut_1': x_asciify__mutmut_1, 
    'x_asciify__mutmut_2': x_asciify__mutmut_2, 
    'x_asciify__mutmut_3': x_asciify__mutmut_3, 
    'x_asciify__mutmut_4': x_asciify__mutmut_4, 
    'x_asciify__mutmut_5': x_asciify__mutmut_5, 
    'x_asciify__mutmut_6': x_asciify__mutmut_6, 
    'x_asciify__mutmut_7': x_asciify__mutmut_7, 
    'x_asciify__mutmut_8': x_asciify__mutmut_8, 
    'x_asciify__mutmut_9': x_asciify__mutmut_9, 
    'x_asciify__mutmut_10': x_asciify__mutmut_10, 
    'x_asciify__mutmut_11': x_asciify__mutmut_11, 
    'x_asciify__mutmut_12': x_asciify__mutmut_12, 
    'x_asciify__mutmut_13': x_asciify__mutmut_13, 
    'x_asciify__mutmut_14': x_asciify__mutmut_14, 
    'x_asciify__mutmut_15': x_asciify__mutmut_15, 
    'x_asciify__mutmut_16': x_asciify__mutmut_16, 
    'x_asciify__mutmut_17': x_asciify__mutmut_17, 
    'x_asciify__mutmut_18': x_asciify__mutmut_18, 
    'x_asciify__mutmut_19': x_asciify__mutmut_19, 
    'x_asciify__mutmut_20': x_asciify__mutmut_20, 
    'x_asciify__mutmut_21': x_asciify__mutmut_21, 
    'x_asciify__mutmut_22': x_asciify__mutmut_22, 
    'x_asciify__mutmut_23': x_asciify__mutmut_23, 
    'x_asciify__mutmut_24': x_asciify__mutmut_24, 
    'x_asciify__mutmut_25': x_asciify__mutmut_25, 
    'x_asciify__mutmut_26': x_asciify__mutmut_26, 
    'x_asciify__mutmut_27': x_asciify__mutmut_27, 
    'x_asciify__mutmut_28': x_asciify__mutmut_28, 
    'x_asciify__mutmut_29': x_asciify__mutmut_29, 
    'x_asciify__mutmut_30': x_asciify__mutmut_30, 
    'x_asciify__mutmut_31': x_asciify__mutmut_31, 
    'x_asciify__mutmut_32': x_asciify__mutmut_32
}

def asciify(*args, **kwargs):
    result = _mutmut_trampoline(x_asciify__mutmut_orig, x_asciify__mutmut_mutants, args, kwargs)
    return result 

asciify.__signature__ = _mutmut_signature(x_asciify__mutmut_orig)
x_asciify__mutmut_orig.__name__ = 'x_asciify'


def x_is_ascii__mutmut_orig(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_1(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode(None)
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_2(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('XXasciiXX')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_3(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ASCII')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_4(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return True
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_5(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode(None)
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_6(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('XXasciiXX')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_7(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ASCII')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_8(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return True
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


def x_is_ascii__mutmut_9(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError(None)
    return True


def x_is_ascii__mutmut_10(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' / type(text))
    return True


def x_is_ascii__mutmut_11(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('XXexpected text or bytes, not %rXX' % type(text))
    return True


def x_is_ascii__mutmut_12(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('EXPECTED TEXT OR BYTES, NOT %R' % type(text))
    return True


def x_is_ascii__mutmut_13(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(None))
    return True


def x_is_ascii__mutmut_14(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return False

x_is_ascii__mutmut_mutants : ClassVar[MutantDict] = {
'x_is_ascii__mutmut_1': x_is_ascii__mutmut_1, 
    'x_is_ascii__mutmut_2': x_is_ascii__mutmut_2, 
    'x_is_ascii__mutmut_3': x_is_ascii__mutmut_3, 
    'x_is_ascii__mutmut_4': x_is_ascii__mutmut_4, 
    'x_is_ascii__mutmut_5': x_is_ascii__mutmut_5, 
    'x_is_ascii__mutmut_6': x_is_ascii__mutmut_6, 
    'x_is_ascii__mutmut_7': x_is_ascii__mutmut_7, 
    'x_is_ascii__mutmut_8': x_is_ascii__mutmut_8, 
    'x_is_ascii__mutmut_9': x_is_ascii__mutmut_9, 
    'x_is_ascii__mutmut_10': x_is_ascii__mutmut_10, 
    'x_is_ascii__mutmut_11': x_is_ascii__mutmut_11, 
    'x_is_ascii__mutmut_12': x_is_ascii__mutmut_12, 
    'x_is_ascii__mutmut_13': x_is_ascii__mutmut_13, 
    'x_is_ascii__mutmut_14': x_is_ascii__mutmut_14
}

def is_ascii(*args, **kwargs):
    result = _mutmut_trampoline(x_is_ascii__mutmut_orig, x_is_ascii__mutmut_mutants, args, kwargs)
    return result 

is_ascii.__signature__ = _mutmut_signature(x_is_ascii__mutmut_orig)
x_is_ascii__mutmut_orig.__name__ = 'x_is_ascii'


class DeaccenterDict(dict):
    "A small caching dictionary for deaccenting."
    def xǁDeaccenterDictǁ__missing____mutmut_orig(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_1(self, key):
        ch = None
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_2(self, key):
        ch = self.get(None)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_3(self, key):
        ch = self.get(key)
        if ch is None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_4(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = None
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_5(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(None)
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_6(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(None))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_7(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = None
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_8(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(None)
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_9(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.partition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_10(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition('XX XX')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_11(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(None, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_12(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, None) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_13(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_14(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, ) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_15(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 17) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_16(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) != 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_17(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 777:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_18(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = None
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_19(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(None)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_20(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = None
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_21(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(None, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_22(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, None)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_23(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_24(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, )
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_25(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 17)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_26(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = None
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_27(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(None, key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_28(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, None)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_29(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key)
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_30(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, )
        self[key] = ch
        return ch
    def xǁDeaccenterDictǁ__missing____mutmut_31(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = None
        return ch
    
    xǁDeaccenterDictǁ__missing____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeaccenterDictǁ__missing____mutmut_1': xǁDeaccenterDictǁ__missing____mutmut_1, 
        'xǁDeaccenterDictǁ__missing____mutmut_2': xǁDeaccenterDictǁ__missing____mutmut_2, 
        'xǁDeaccenterDictǁ__missing____mutmut_3': xǁDeaccenterDictǁ__missing____mutmut_3, 
        'xǁDeaccenterDictǁ__missing____mutmut_4': xǁDeaccenterDictǁ__missing____mutmut_4, 
        'xǁDeaccenterDictǁ__missing____mutmut_5': xǁDeaccenterDictǁ__missing____mutmut_5, 
        'xǁDeaccenterDictǁ__missing____mutmut_6': xǁDeaccenterDictǁ__missing____mutmut_6, 
        'xǁDeaccenterDictǁ__missing____mutmut_7': xǁDeaccenterDictǁ__missing____mutmut_7, 
        'xǁDeaccenterDictǁ__missing____mutmut_8': xǁDeaccenterDictǁ__missing____mutmut_8, 
        'xǁDeaccenterDictǁ__missing____mutmut_9': xǁDeaccenterDictǁ__missing____mutmut_9, 
        'xǁDeaccenterDictǁ__missing____mutmut_10': xǁDeaccenterDictǁ__missing____mutmut_10, 
        'xǁDeaccenterDictǁ__missing____mutmut_11': xǁDeaccenterDictǁ__missing____mutmut_11, 
        'xǁDeaccenterDictǁ__missing____mutmut_12': xǁDeaccenterDictǁ__missing____mutmut_12, 
        'xǁDeaccenterDictǁ__missing____mutmut_13': xǁDeaccenterDictǁ__missing____mutmut_13, 
        'xǁDeaccenterDictǁ__missing____mutmut_14': xǁDeaccenterDictǁ__missing____mutmut_14, 
        'xǁDeaccenterDictǁ__missing____mutmut_15': xǁDeaccenterDictǁ__missing____mutmut_15, 
        'xǁDeaccenterDictǁ__missing____mutmut_16': xǁDeaccenterDictǁ__missing____mutmut_16, 
        'xǁDeaccenterDictǁ__missing____mutmut_17': xǁDeaccenterDictǁ__missing____mutmut_17, 
        'xǁDeaccenterDictǁ__missing____mutmut_18': xǁDeaccenterDictǁ__missing____mutmut_18, 
        'xǁDeaccenterDictǁ__missing____mutmut_19': xǁDeaccenterDictǁ__missing____mutmut_19, 
        'xǁDeaccenterDictǁ__missing____mutmut_20': xǁDeaccenterDictǁ__missing____mutmut_20, 
        'xǁDeaccenterDictǁ__missing____mutmut_21': xǁDeaccenterDictǁ__missing____mutmut_21, 
        'xǁDeaccenterDictǁ__missing____mutmut_22': xǁDeaccenterDictǁ__missing____mutmut_22, 
        'xǁDeaccenterDictǁ__missing____mutmut_23': xǁDeaccenterDictǁ__missing____mutmut_23, 
        'xǁDeaccenterDictǁ__missing____mutmut_24': xǁDeaccenterDictǁ__missing____mutmut_24, 
        'xǁDeaccenterDictǁ__missing____mutmut_25': xǁDeaccenterDictǁ__missing____mutmut_25, 
        'xǁDeaccenterDictǁ__missing____mutmut_26': xǁDeaccenterDictǁ__missing____mutmut_26, 
        'xǁDeaccenterDictǁ__missing____mutmut_27': xǁDeaccenterDictǁ__missing____mutmut_27, 
        'xǁDeaccenterDictǁ__missing____mutmut_28': xǁDeaccenterDictǁ__missing____mutmut_28, 
        'xǁDeaccenterDictǁ__missing____mutmut_29': xǁDeaccenterDictǁ__missing____mutmut_29, 
        'xǁDeaccenterDictǁ__missing____mutmut_30': xǁDeaccenterDictǁ__missing____mutmut_30, 
        'xǁDeaccenterDictǁ__missing____mutmut_31': xǁDeaccenterDictǁ__missing____mutmut_31
    }
    
    def __missing__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeaccenterDictǁ__missing____mutmut_orig"), object.__getattribute__(self, "xǁDeaccenterDictǁ__missing____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __missing__.__signature__ = _mutmut_signature(xǁDeaccenterDictǁ__missing____mutmut_orig)
    xǁDeaccenterDictǁ__missing____mutmut_orig.__name__ = 'xǁDeaccenterDictǁ__missing__'


# http://chmullig.com/2009/12/python-unicode-ascii-ifier/
# For something more complete, investigate the unidecode
# or isounidecode packages, which are capable of performing
# crude transliteration.
_BASE_DEACCENT_MAP = {
    0xc6: "AE", # Æ LATIN CAPITAL LETTER AE
    0xd0: "D",  # Ð LATIN CAPITAL LETTER ETH
    0xd8: "OE", # Ø LATIN CAPITAL LETTER O WITH STROKE
    0xde: "Th", # Þ LATIN CAPITAL LETTER THORN
    0xc4: 'Ae', # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
    0xd6: 'Oe', # Ö LATIN CAPITAL LETTER O WITH DIAERESIS
    0xdc: 'Ue', # Ü LATIN CAPITAL LETTER U WITH DIAERESIS
    0xc0: "A",  # À LATIN CAPITAL LETTER A WITH GRAVE
    0xc1: "A",  # Á LATIN CAPITAL LETTER A WITH ACUTE
    0xc3: "A",  # Ã LATIN CAPITAL LETTER A WITH TILDE
    0xc7: "C",  # Ç LATIN CAPITAL LETTER C WITH CEDILLA
    0xc8: "E",  # È LATIN CAPITAL LETTER E WITH GRAVE
    0xc9: "E",  # É LATIN CAPITAL LETTER E WITH ACUTE
    0xca: "E",  # Ê LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xcc: "I",  # Ì LATIN CAPITAL LETTER I WITH GRAVE
    0xcd: "I",  # Í LATIN CAPITAL LETTER I WITH ACUTE
    0xd2: "O",  # Ò LATIN CAPITAL LETTER O WITH GRAVE
    0xd3: "O",  # Ó LATIN CAPITAL LETTER O WITH ACUTE
    0xd5: "O",  # Õ LATIN CAPITAL LETTER O WITH TILDE
    0xd9: "U",  # Ù LATIN CAPITAL LETTER U WITH GRAVE
    0xda: "U",  # Ú LATIN CAPITAL LETTER U WITH ACUTE
    0xdf: "ss", # ß LATIN SMALL LETTER SHARP S
    0xe6: "ae", # æ LATIN SMALL LETTER AE
    0xf0: "d",  # ð LATIN SMALL LETTER ETH
    0xf8: "oe", # ø LATIN SMALL LETTER O WITH STROKE
    0xfe: "th", # þ LATIN SMALL LETTER THORN,
    0xe4: 'ae', # ä LATIN SMALL LETTER A WITH DIAERESIS
    0xf6: 'oe', # ö LATIN SMALL LETTER O WITH DIAERESIS
    0xfc: 'ue', # ü LATIN SMALL LETTER U WITH DIAERESIS
    0xe0: "a",  # à LATIN SMALL LETTER A WITH GRAVE
    0xe1: "a",  # á LATIN SMALL LETTER A WITH ACUTE
    0xe3: "a",  # ã LATIN SMALL LETTER A WITH TILDE
    0xe7: "c",  # ç LATIN SMALL LETTER C WITH CEDILLA
    0xe8: "e",  # è LATIN SMALL LETTER E WITH GRAVE
    0xe9: "e",  # é LATIN SMALL LETTER E WITH ACUTE
    0xea: "e",  # ê LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xec: "i",  # ì LATIN SMALL LETTER I WITH GRAVE
    0xed: "i",  # í LATIN SMALL LETTER I WITH ACUTE
    0xf2: "o",  # ò LATIN SMALL LETTER O WITH GRAVE
    0xf3: "o",  # ó LATIN SMALL LETTER O WITH ACUTE
    0xf5: "o",  # õ LATIN SMALL LETTER O WITH TILDE
    0xf9: "u",  # ù LATIN SMALL LETTER U WITH GRAVE
    0xfa: "u",  # ú LATIN SMALL LETTER U WITH ACUTE
    0x2018: "'",  # ‘ LEFT SINGLE QUOTATION MARK
    0x2019: "'",  # ’ RIGHT SINGLE QUOTATION MARK
    0x201c: '"',  # “ LEFT DOUBLE QUOTATION MARK
    0x201d: '"',  # ” RIGHT DOUBLE QUOTATION MARK
    }


DEACCENT_MAP = DeaccenterDict(_BASE_DEACCENT_MAP)


_SIZE_SYMBOLS = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
_SIZE_BOUNDS = [(1024 ** i, sym) for i, sym in enumerate(_SIZE_SYMBOLS)]
_SIZE_RANGES = list(zip(_SIZE_BOUNDS, _SIZE_BOUNDS[1:]))


def x_bytes2human__mutmut_orig(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_1(nbytes, ndigits=1):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_2(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = None
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_3(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(None)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_4(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes < next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_5(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            return
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_6(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = None
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_7(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) * size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_8(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(None) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_9(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=None,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_10(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=None,
                                                  symbol=symbol)


def x_bytes2human__mutmut_11(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=None)


def x_bytes2human__mutmut_12(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_13(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  symbol=symbol)


def x_bytes2human__mutmut_14(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  )


def x_bytes2human__mutmut_15(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return 'XX{hnbytes:.{ndigits}f}{symbol}XX'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


def x_bytes2human__mutmut_16(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{HNBYTES:.{NDIGITS}F}{SYMBOL}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)

x_bytes2human__mutmut_mutants : ClassVar[MutantDict] = {
'x_bytes2human__mutmut_1': x_bytes2human__mutmut_1, 
    'x_bytes2human__mutmut_2': x_bytes2human__mutmut_2, 
    'x_bytes2human__mutmut_3': x_bytes2human__mutmut_3, 
    'x_bytes2human__mutmut_4': x_bytes2human__mutmut_4, 
    'x_bytes2human__mutmut_5': x_bytes2human__mutmut_5, 
    'x_bytes2human__mutmut_6': x_bytes2human__mutmut_6, 
    'x_bytes2human__mutmut_7': x_bytes2human__mutmut_7, 
    'x_bytes2human__mutmut_8': x_bytes2human__mutmut_8, 
    'x_bytes2human__mutmut_9': x_bytes2human__mutmut_9, 
    'x_bytes2human__mutmut_10': x_bytes2human__mutmut_10, 
    'x_bytes2human__mutmut_11': x_bytes2human__mutmut_11, 
    'x_bytes2human__mutmut_12': x_bytes2human__mutmut_12, 
    'x_bytes2human__mutmut_13': x_bytes2human__mutmut_13, 
    'x_bytes2human__mutmut_14': x_bytes2human__mutmut_14, 
    'x_bytes2human__mutmut_15': x_bytes2human__mutmut_15, 
    'x_bytes2human__mutmut_16': x_bytes2human__mutmut_16
}

def bytes2human(*args, **kwargs):
    result = _mutmut_trampoline(x_bytes2human__mutmut_orig, x_bytes2human__mutmut_mutants, args, kwargs)
    return result 

bytes2human.__signature__ = _mutmut_signature(x_bytes2human__mutmut_orig)
x_bytes2human__mutmut_orig.__name__ = 'x_bytes2human'


class HTMLTextExtractor(HTMLParser):
    def xǁHTMLTextExtractorǁ__init____mutmut_orig(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.result = []
    def xǁHTMLTextExtractorǁ__init____mutmut_1(self):
        self.reset()
        self.strict = None
        self.convert_charrefs = True
        self.result = []
    def xǁHTMLTextExtractorǁ__init____mutmut_2(self):
        self.reset()
        self.strict = True
        self.convert_charrefs = True
        self.result = []
    def xǁHTMLTextExtractorǁ__init____mutmut_3(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = None
        self.result = []
    def xǁHTMLTextExtractorǁ__init____mutmut_4(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = False
        self.result = []
    def xǁHTMLTextExtractorǁ__init____mutmut_5(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.result = None
    
    xǁHTMLTextExtractorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLTextExtractorǁ__init____mutmut_1': xǁHTMLTextExtractorǁ__init____mutmut_1, 
        'xǁHTMLTextExtractorǁ__init____mutmut_2': xǁHTMLTextExtractorǁ__init____mutmut_2, 
        'xǁHTMLTextExtractorǁ__init____mutmut_3': xǁHTMLTextExtractorǁ__init____mutmut_3, 
        'xǁHTMLTextExtractorǁ__init____mutmut_4': xǁHTMLTextExtractorǁ__init____mutmut_4, 
        'xǁHTMLTextExtractorǁ__init____mutmut_5': xǁHTMLTextExtractorǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLTextExtractorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁHTMLTextExtractorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁHTMLTextExtractorǁ__init____mutmut_orig)
    xǁHTMLTextExtractorǁ__init____mutmut_orig.__name__ = 'xǁHTMLTextExtractorǁ__init__'

    def xǁHTMLTextExtractorǁhandle_data__mutmut_orig(self, d):
        self.result.append(d)

    def xǁHTMLTextExtractorǁhandle_data__mutmut_1(self, d):
        self.result.append(None)
    
    xǁHTMLTextExtractorǁhandle_data__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLTextExtractorǁhandle_data__mutmut_1': xǁHTMLTextExtractorǁhandle_data__mutmut_1
    }
    
    def handle_data(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_data__mutmut_orig"), object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_data__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_data.__signature__ = _mutmut_signature(xǁHTMLTextExtractorǁhandle_data__mutmut_orig)
    xǁHTMLTextExtractorǁhandle_data__mutmut_orig.__name__ = 'xǁHTMLTextExtractorǁhandle_data'

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_orig(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_1(self, number):
        if number[0] == 'x' and number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_2(self, number):
        if number[1] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_3(self, number):
        if number[0] != 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_4(self, number):
        if number[0] == 'XXxXX' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_5(self, number):
        if number[0] == 'X' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_6(self, number):
        if number[0] == 'x' or number[1] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_7(self, number):
        if number[0] == 'x' or number[0] != 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_8(self, number):
        if number[0] == 'x' or number[0] == 'XXXXX':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_9(self, number):
        if number[0] == 'x' or number[0] == 'x':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_10(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = None
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_11(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(None, 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_12(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], None)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_13(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_14(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], )
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_15(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[2:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_16(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 17)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_17(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = None
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_18(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(None)
        self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_19(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(None)

    def xǁHTMLTextExtractorǁhandle_charref__mutmut_20(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(None))
    
    xǁHTMLTextExtractorǁhandle_charref__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLTextExtractorǁhandle_charref__mutmut_1': xǁHTMLTextExtractorǁhandle_charref__mutmut_1, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_2': xǁHTMLTextExtractorǁhandle_charref__mutmut_2, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_3': xǁHTMLTextExtractorǁhandle_charref__mutmut_3, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_4': xǁHTMLTextExtractorǁhandle_charref__mutmut_4, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_5': xǁHTMLTextExtractorǁhandle_charref__mutmut_5, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_6': xǁHTMLTextExtractorǁhandle_charref__mutmut_6, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_7': xǁHTMLTextExtractorǁhandle_charref__mutmut_7, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_8': xǁHTMLTextExtractorǁhandle_charref__mutmut_8, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_9': xǁHTMLTextExtractorǁhandle_charref__mutmut_9, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_10': xǁHTMLTextExtractorǁhandle_charref__mutmut_10, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_11': xǁHTMLTextExtractorǁhandle_charref__mutmut_11, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_12': xǁHTMLTextExtractorǁhandle_charref__mutmut_12, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_13': xǁHTMLTextExtractorǁhandle_charref__mutmut_13, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_14': xǁHTMLTextExtractorǁhandle_charref__mutmut_14, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_15': xǁHTMLTextExtractorǁhandle_charref__mutmut_15, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_16': xǁHTMLTextExtractorǁhandle_charref__mutmut_16, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_17': xǁHTMLTextExtractorǁhandle_charref__mutmut_17, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_18': xǁHTMLTextExtractorǁhandle_charref__mutmut_18, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_19': xǁHTMLTextExtractorǁhandle_charref__mutmut_19, 
        'xǁHTMLTextExtractorǁhandle_charref__mutmut_20': xǁHTMLTextExtractorǁhandle_charref__mutmut_20
    }
    
    def handle_charref(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_charref__mutmut_orig"), object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_charref__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_charref.__signature__ = _mutmut_signature(xǁHTMLTextExtractorǁhandle_charref__mutmut_orig)
    xǁHTMLTextExtractorǁhandle_charref__mutmut_orig.__name__ = 'xǁHTMLTextExtractorǁhandle_charref'

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_orig(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name + ';')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_1(self, name):
        try:
            codepoint = None
        except KeyError:
            self.result.append('&' + name + ';')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_2(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append(None)
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_3(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name - ';')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_4(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' - name + ';')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_5(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('XX&XX' + name + ';')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_6(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name + 'XX;XX')
        else:
            self.result.append(chr(codepoint))

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_7(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name + ';')
        else:
            self.result.append(None)

    def xǁHTMLTextExtractorǁhandle_entityref__mutmut_8(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name + ';')
        else:
            self.result.append(chr(None))
    
    xǁHTMLTextExtractorǁhandle_entityref__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLTextExtractorǁhandle_entityref__mutmut_1': xǁHTMLTextExtractorǁhandle_entityref__mutmut_1, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_2': xǁHTMLTextExtractorǁhandle_entityref__mutmut_2, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_3': xǁHTMLTextExtractorǁhandle_entityref__mutmut_3, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_4': xǁHTMLTextExtractorǁhandle_entityref__mutmut_4, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_5': xǁHTMLTextExtractorǁhandle_entityref__mutmut_5, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_6': xǁHTMLTextExtractorǁhandle_entityref__mutmut_6, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_7': xǁHTMLTextExtractorǁhandle_entityref__mutmut_7, 
        'xǁHTMLTextExtractorǁhandle_entityref__mutmut_8': xǁHTMLTextExtractorǁhandle_entityref__mutmut_8
    }
    
    def handle_entityref(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_entityref__mutmut_orig"), object.__getattribute__(self, "xǁHTMLTextExtractorǁhandle_entityref__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_entityref.__signature__ = _mutmut_signature(xǁHTMLTextExtractorǁhandle_entityref__mutmut_orig)
    xǁHTMLTextExtractorǁhandle_entityref__mutmut_orig.__name__ = 'xǁHTMLTextExtractorǁhandle_entityref'

    def xǁHTMLTextExtractorǁget_text__mutmut_orig(self):
        return ''.join(self.result)

    def xǁHTMLTextExtractorǁget_text__mutmut_1(self):
        return ''.join(None)

    def xǁHTMLTextExtractorǁget_text__mutmut_2(self):
        return 'XXXX'.join(self.result)
    
    xǁHTMLTextExtractorǁget_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLTextExtractorǁget_text__mutmut_1': xǁHTMLTextExtractorǁget_text__mutmut_1, 
        'xǁHTMLTextExtractorǁget_text__mutmut_2': xǁHTMLTextExtractorǁget_text__mutmut_2
    }
    
    def get_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLTextExtractorǁget_text__mutmut_orig"), object.__getattribute__(self, "xǁHTMLTextExtractorǁget_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_text.__signature__ = _mutmut_signature(xǁHTMLTextExtractorǁget_text__mutmut_orig)
    xǁHTMLTextExtractorǁget_text__mutmut_orig.__name__ = 'xǁHTMLTextExtractorǁget_text'


def x_html2text__mutmut_orig(html):
    """Strips tags from HTML text, returning markup-free text. Also, does
    a best effort replacement of entities like "&nbsp;"

    >>> r = html2text(u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>')
    >>> r == u'Test &(\u0394\u03b7\u03bc\u03ce)'
    True
    """
    # based on answers to http://stackoverflow.com/questions/753052/
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


def x_html2text__mutmut_1(html):
    """Strips tags from HTML text, returning markup-free text. Also, does
    a best effort replacement of entities like "&nbsp;"

    >>> r = html2text(u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>')
    >>> r == u'Test &(\u0394\u03b7\u03bc\u03ce)'
    True
    """
    # based on answers to http://stackoverflow.com/questions/753052/
    s = None
    s.feed(html)
    return s.get_text()


def x_html2text__mutmut_2(html):
    """Strips tags from HTML text, returning markup-free text. Also, does
    a best effort replacement of entities like "&nbsp;"

    >>> r = html2text(u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>')
    >>> r == u'Test &(\u0394\u03b7\u03bc\u03ce)'
    True
    """
    # based on answers to http://stackoverflow.com/questions/753052/
    s = HTMLTextExtractor()
    s.feed(None)
    return s.get_text()

x_html2text__mutmut_mutants : ClassVar[MutantDict] = {
'x_html2text__mutmut_1': x_html2text__mutmut_1, 
    'x_html2text__mutmut_2': x_html2text__mutmut_2
}

def html2text(*args, **kwargs):
    result = _mutmut_trampoline(x_html2text__mutmut_orig, x_html2text__mutmut_mutants, args, kwargs)
    return result 

html2text.__signature__ = _mutmut_signature(x_html2text__mutmut_orig)
x_html2text__mutmut_orig.__name__ = 'x_html2text'


_EMPTY_GZIP_BYTES = b'\x1f\x8b\x08\x089\xf3\xb9U\x00\x03empty\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00'
_NON_EMPTY_GZIP_BYTES = b'\x1f\x8b\x08\x08\xbc\xf7\xb9U\x00\x03not_empty\x00K\xaa,I-N\xcc\xc8\xafT\xe4\x02\x00\xf3nb\xbf\x0b\x00\x00\x00'


def x_gunzip_bytes__mutmut_orig(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, 16 + zlib.MAX_WBITS)


def x_gunzip_bytes__mutmut_1(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(None, 16 + zlib.MAX_WBITS)


def x_gunzip_bytes__mutmut_2(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, None)


def x_gunzip_bytes__mutmut_3(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(16 + zlib.MAX_WBITS)


def x_gunzip_bytes__mutmut_4(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, )


def x_gunzip_bytes__mutmut_5(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, 16 - zlib.MAX_WBITS)


def x_gunzip_bytes__mutmut_6(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, 17 + zlib.MAX_WBITS)

x_gunzip_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x_gunzip_bytes__mutmut_1': x_gunzip_bytes__mutmut_1, 
    'x_gunzip_bytes__mutmut_2': x_gunzip_bytes__mutmut_2, 
    'x_gunzip_bytes__mutmut_3': x_gunzip_bytes__mutmut_3, 
    'x_gunzip_bytes__mutmut_4': x_gunzip_bytes__mutmut_4, 
    'x_gunzip_bytes__mutmut_5': x_gunzip_bytes__mutmut_5, 
    'x_gunzip_bytes__mutmut_6': x_gunzip_bytes__mutmut_6
}

def gunzip_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x_gunzip_bytes__mutmut_orig, x_gunzip_bytes__mutmut_mutants, args, kwargs)
    return result 

gunzip_bytes.__signature__ = _mutmut_signature(x_gunzip_bytes__mutmut_orig)
x_gunzip_bytes__mutmut_orig.__name__ = 'x_gunzip_bytes'


def x_gzip_bytes__mutmut_orig(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_1(bytestring, level=7):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_2(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = None
    f = GzipFile(fileobj=out, mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_3(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = None
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_4(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=None, mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_5(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode=None, compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_6(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', compresslevel=None)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_7(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_8(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_9(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', )
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_10(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='XXwbXX', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_11(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='WB', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()


def x_gzip_bytes__mutmut_12(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', compresslevel=level)
    f.write(None)
    f.close()
    return out.getvalue()

x_gzip_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x_gzip_bytes__mutmut_1': x_gzip_bytes__mutmut_1, 
    'x_gzip_bytes__mutmut_2': x_gzip_bytes__mutmut_2, 
    'x_gzip_bytes__mutmut_3': x_gzip_bytes__mutmut_3, 
    'x_gzip_bytes__mutmut_4': x_gzip_bytes__mutmut_4, 
    'x_gzip_bytes__mutmut_5': x_gzip_bytes__mutmut_5, 
    'x_gzip_bytes__mutmut_6': x_gzip_bytes__mutmut_6, 
    'x_gzip_bytes__mutmut_7': x_gzip_bytes__mutmut_7, 
    'x_gzip_bytes__mutmut_8': x_gzip_bytes__mutmut_8, 
    'x_gzip_bytes__mutmut_9': x_gzip_bytes__mutmut_9, 
    'x_gzip_bytes__mutmut_10': x_gzip_bytes__mutmut_10, 
    'x_gzip_bytes__mutmut_11': x_gzip_bytes__mutmut_11, 
    'x_gzip_bytes__mutmut_12': x_gzip_bytes__mutmut_12
}

def gzip_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x_gzip_bytes__mutmut_orig, x_gzip_bytes__mutmut_mutants, args, kwargs)
    return result 

gzip_bytes.__signature__ = _mutmut_signature(x_gzip_bytes__mutmut_orig)
x_gzip_bytes__mutmut_orig.__name__ = 'x_gzip_bytes'



_line_ending_re = re.compile(r'(\r\n|\n|\x0b|\f|\r|\x85|\x2028|\x2029)',
                             re.UNICODE)


def x_iter_splitlines__mutmut_orig(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_1(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = None
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_2(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 1, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_3(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(None):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_4(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = None
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_5(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(None), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_6(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(2), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_7(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(None)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_8(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(2)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_9(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end < start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_10(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end != len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_11(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield 'XXXX'
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_12(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = None
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def x_iter_splitlines__mutmut_13(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = None
    if tail:
        yield tail
    return

x_iter_splitlines__mutmut_mutants : ClassVar[MutantDict] = {
'x_iter_splitlines__mutmut_1': x_iter_splitlines__mutmut_1, 
    'x_iter_splitlines__mutmut_2': x_iter_splitlines__mutmut_2, 
    'x_iter_splitlines__mutmut_3': x_iter_splitlines__mutmut_3, 
    'x_iter_splitlines__mutmut_4': x_iter_splitlines__mutmut_4, 
    'x_iter_splitlines__mutmut_5': x_iter_splitlines__mutmut_5, 
    'x_iter_splitlines__mutmut_6': x_iter_splitlines__mutmut_6, 
    'x_iter_splitlines__mutmut_7': x_iter_splitlines__mutmut_7, 
    'x_iter_splitlines__mutmut_8': x_iter_splitlines__mutmut_8, 
    'x_iter_splitlines__mutmut_9': x_iter_splitlines__mutmut_9, 
    'x_iter_splitlines__mutmut_10': x_iter_splitlines__mutmut_10, 
    'x_iter_splitlines__mutmut_11': x_iter_splitlines__mutmut_11, 
    'x_iter_splitlines__mutmut_12': x_iter_splitlines__mutmut_12, 
    'x_iter_splitlines__mutmut_13': x_iter_splitlines__mutmut_13
}

def iter_splitlines(*args, **kwargs):
    result = _mutmut_trampoline(x_iter_splitlines__mutmut_orig, x_iter_splitlines__mutmut_mutants, args, kwargs)
    return result 

iter_splitlines.__signature__ = _mutmut_signature(x_iter_splitlines__mutmut_orig)
x_iter_splitlines__mutmut_orig.__name__ = 'x_iter_splitlines'


def x_indent__mutmut_orig(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(line) else line)
                      for line in iter_splitlines(text)]
    return newline.join(indented_lines)


def x_indent__mutmut_1(text, margin, newline='XX\nXX', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(line) else line)
                      for line in iter_splitlines(text)]
    return newline.join(indented_lines)


def x_indent__mutmut_2(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = None
    return newline.join(indented_lines)


def x_indent__mutmut_3(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin - line if key(line) else line)
                      for line in iter_splitlines(text)]
    return newline.join(indented_lines)


def x_indent__mutmut_4(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(None) else line)
                      for line in iter_splitlines(text)]
    return newline.join(indented_lines)


def x_indent__mutmut_5(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(line) else line)
                      for line in iter_splitlines(None)]
    return newline.join(indented_lines)


def x_indent__mutmut_6(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(line) else line)
                      for line in iter_splitlines(text)]
    return newline.join(None)

x_indent__mutmut_mutants : ClassVar[MutantDict] = {
'x_indent__mutmut_1': x_indent__mutmut_1, 
    'x_indent__mutmut_2': x_indent__mutmut_2, 
    'x_indent__mutmut_3': x_indent__mutmut_3, 
    'x_indent__mutmut_4': x_indent__mutmut_4, 
    'x_indent__mutmut_5': x_indent__mutmut_5, 
    'x_indent__mutmut_6': x_indent__mutmut_6
}

def indent(*args, **kwargs):
    result = _mutmut_trampoline(x_indent__mutmut_orig, x_indent__mutmut_mutants, args, kwargs)
    return result 

indent.__signature__ = _mutmut_signature(x_indent__mutmut_orig)
x_indent__mutmut_orig.__name__ = 'x_indent'


def x_is_uuid__mutmut_orig(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_1(obj, version=5):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_2(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_3(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = None
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_4(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(None)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_5(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return True
    if version and obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_6(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version or obj.version != int(version):
        return False
    return True


def x_is_uuid__mutmut_7(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version == int(version):
        return False
    return True


def x_is_uuid__mutmut_8(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(None):
        return False
    return True


def x_is_uuid__mutmut_9(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return True
    return True


def x_is_uuid__mutmut_10(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return False

x_is_uuid__mutmut_mutants : ClassVar[MutantDict] = {
'x_is_uuid__mutmut_1': x_is_uuid__mutmut_1, 
    'x_is_uuid__mutmut_2': x_is_uuid__mutmut_2, 
    'x_is_uuid__mutmut_3': x_is_uuid__mutmut_3, 
    'x_is_uuid__mutmut_4': x_is_uuid__mutmut_4, 
    'x_is_uuid__mutmut_5': x_is_uuid__mutmut_5, 
    'x_is_uuid__mutmut_6': x_is_uuid__mutmut_6, 
    'x_is_uuid__mutmut_7': x_is_uuid__mutmut_7, 
    'x_is_uuid__mutmut_8': x_is_uuid__mutmut_8, 
    'x_is_uuid__mutmut_9': x_is_uuid__mutmut_9, 
    'x_is_uuid__mutmut_10': x_is_uuid__mutmut_10
}

def is_uuid(*args, **kwargs):
    result = _mutmut_trampoline(x_is_uuid__mutmut_orig, x_is_uuid__mutmut_mutants, args, kwargs)
    return result 

is_uuid.__signature__ = _mutmut_signature(x_is_uuid__mutmut_orig)
x_is_uuid__mutmut_orig.__name__ = 'x_is_uuid'


def x_escape_shell_args__mutmut_orig(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_1(args, sep='XX XX', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_2(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_3(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = None

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_4(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'XXcmdXX' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_5(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'CMD' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_6(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform != 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_7(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'XXwin32XX' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_8(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'WIN32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_9(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'XXshXX'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_10(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'SH'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_11(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style != 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_12(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'XXshXX':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_13(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'SH':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_14(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(None, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_15(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=None)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_16(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_17(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, )
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_18(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style != 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_19(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'XXcmdXX':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_20(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'CMD':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_21(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(None, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_22(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=None)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_23(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_24(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, )

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


def x_escape_shell_args__mutmut_25(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError(None)


def x_escape_shell_args__mutmut_26(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" / style)


def x_escape_shell_args__mutmut_27(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("XXstyle expected one of 'cmd' or 'sh', not %rXX" % style)


def x_escape_shell_args__mutmut_28(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("STYLE EXPECTED ONE OF 'CMD' OR 'SH', NOT %R" % style)

x_escape_shell_args__mutmut_mutants : ClassVar[MutantDict] = {
'x_escape_shell_args__mutmut_1': x_escape_shell_args__mutmut_1, 
    'x_escape_shell_args__mutmut_2': x_escape_shell_args__mutmut_2, 
    'x_escape_shell_args__mutmut_3': x_escape_shell_args__mutmut_3, 
    'x_escape_shell_args__mutmut_4': x_escape_shell_args__mutmut_4, 
    'x_escape_shell_args__mutmut_5': x_escape_shell_args__mutmut_5, 
    'x_escape_shell_args__mutmut_6': x_escape_shell_args__mutmut_6, 
    'x_escape_shell_args__mutmut_7': x_escape_shell_args__mutmut_7, 
    'x_escape_shell_args__mutmut_8': x_escape_shell_args__mutmut_8, 
    'x_escape_shell_args__mutmut_9': x_escape_shell_args__mutmut_9, 
    'x_escape_shell_args__mutmut_10': x_escape_shell_args__mutmut_10, 
    'x_escape_shell_args__mutmut_11': x_escape_shell_args__mutmut_11, 
    'x_escape_shell_args__mutmut_12': x_escape_shell_args__mutmut_12, 
    'x_escape_shell_args__mutmut_13': x_escape_shell_args__mutmut_13, 
    'x_escape_shell_args__mutmut_14': x_escape_shell_args__mutmut_14, 
    'x_escape_shell_args__mutmut_15': x_escape_shell_args__mutmut_15, 
    'x_escape_shell_args__mutmut_16': x_escape_shell_args__mutmut_16, 
    'x_escape_shell_args__mutmut_17': x_escape_shell_args__mutmut_17, 
    'x_escape_shell_args__mutmut_18': x_escape_shell_args__mutmut_18, 
    'x_escape_shell_args__mutmut_19': x_escape_shell_args__mutmut_19, 
    'x_escape_shell_args__mutmut_20': x_escape_shell_args__mutmut_20, 
    'x_escape_shell_args__mutmut_21': x_escape_shell_args__mutmut_21, 
    'x_escape_shell_args__mutmut_22': x_escape_shell_args__mutmut_22, 
    'x_escape_shell_args__mutmut_23': x_escape_shell_args__mutmut_23, 
    'x_escape_shell_args__mutmut_24': x_escape_shell_args__mutmut_24, 
    'x_escape_shell_args__mutmut_25': x_escape_shell_args__mutmut_25, 
    'x_escape_shell_args__mutmut_26': x_escape_shell_args__mutmut_26, 
    'x_escape_shell_args__mutmut_27': x_escape_shell_args__mutmut_27, 
    'x_escape_shell_args__mutmut_28': x_escape_shell_args__mutmut_28
}

def escape_shell_args(*args, **kwargs):
    result = _mutmut_trampoline(x_escape_shell_args__mutmut_orig, x_escape_shell_args__mutmut_mutants, args, kwargs)
    return result 

escape_shell_args.__signature__ = _mutmut_signature(x_escape_shell_args__mutmut_orig)
x_escape_shell_args__mutmut_orig.__name__ = 'x_escape_shell_args'


_find_sh_unsafe = re.compile(r'[^a-zA-Z0-9_@%+=:,./-]').search


def x_args2sh__mutmut_orig(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_1(args, sep='XX XX'):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_2(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = None

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_3(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_4(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append(None)
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_5(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("XX''XX")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_6(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            break
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_7(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(None) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_8(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is not None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_9(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(None)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_10(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            break
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_11(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append(None)

    return ' '.join(ret_list)


def x_args2sh__mutmut_12(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") - "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_13(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" - arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_14(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("XX'XX" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_15(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace(None, "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_16(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", None) + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_17(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_18(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", ) + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_19(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("XX'XX", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_20(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "XX'\"'\"'XX") + "'")

    return ' '.join(ret_list)


def x_args2sh__mutmut_21(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "XX'XX")

    return ' '.join(ret_list)


def x_args2sh__mutmut_22(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(None)


def x_args2sh__mutmut_23(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return 'XX XX'.join(ret_list)

x_args2sh__mutmut_mutants : ClassVar[MutantDict] = {
'x_args2sh__mutmut_1': x_args2sh__mutmut_1, 
    'x_args2sh__mutmut_2': x_args2sh__mutmut_2, 
    'x_args2sh__mutmut_3': x_args2sh__mutmut_3, 
    'x_args2sh__mutmut_4': x_args2sh__mutmut_4, 
    'x_args2sh__mutmut_5': x_args2sh__mutmut_5, 
    'x_args2sh__mutmut_6': x_args2sh__mutmut_6, 
    'x_args2sh__mutmut_7': x_args2sh__mutmut_7, 
    'x_args2sh__mutmut_8': x_args2sh__mutmut_8, 
    'x_args2sh__mutmut_9': x_args2sh__mutmut_9, 
    'x_args2sh__mutmut_10': x_args2sh__mutmut_10, 
    'x_args2sh__mutmut_11': x_args2sh__mutmut_11, 
    'x_args2sh__mutmut_12': x_args2sh__mutmut_12, 
    'x_args2sh__mutmut_13': x_args2sh__mutmut_13, 
    'x_args2sh__mutmut_14': x_args2sh__mutmut_14, 
    'x_args2sh__mutmut_15': x_args2sh__mutmut_15, 
    'x_args2sh__mutmut_16': x_args2sh__mutmut_16, 
    'x_args2sh__mutmut_17': x_args2sh__mutmut_17, 
    'x_args2sh__mutmut_18': x_args2sh__mutmut_18, 
    'x_args2sh__mutmut_19': x_args2sh__mutmut_19, 
    'x_args2sh__mutmut_20': x_args2sh__mutmut_20, 
    'x_args2sh__mutmut_21': x_args2sh__mutmut_21, 
    'x_args2sh__mutmut_22': x_args2sh__mutmut_22, 
    'x_args2sh__mutmut_23': x_args2sh__mutmut_23
}

def args2sh(*args, **kwargs):
    result = _mutmut_trampoline(x_args2sh__mutmut_orig, x_args2sh__mutmut_mutants, args, kwargs)
    return result 

args2sh.__signature__ = _mutmut_signature(x_args2sh__mutmut_orig)
x_args2sh__mutmut_orig.__name__ = 'x_args2sh'


def x_args2cmd__mutmut_orig(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_1(args, sep='XX XX'):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_2(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = None
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_3(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = None
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_4(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = True
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_5(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = None

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_6(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(None)

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_7(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append('XX XX')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_8(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = None
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_9(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) and not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_10(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) and ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_11(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = ("XX XX" in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_12(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " not in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_13(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("XX\tXX" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_14(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" not in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_15(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_16(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append(None)

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_17(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('XX"XX')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_18(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c != '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_19(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == 'XX\\XX':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_20(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(None)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_21(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c != '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_22(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == 'XX"XX':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_23(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append(None)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_24(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf) / 2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_25(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' / len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_26(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('XX\\XX' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_27(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*3)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_28(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = None
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_29(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append(None)
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_30(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('XX\\"XX')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_31(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(None)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_32(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = None
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_33(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(None)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_34(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(None)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_35(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(None)
            result.append('"')

    return ''.join(result)


def x_args2cmd__mutmut_36(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append(None)

    return ''.join(result)


def x_args2cmd__mutmut_37(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('XX"XX')

    return ''.join(result)


def x_args2cmd__mutmut_38(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(None)


def x_args2cmd__mutmut_39(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return 'XXXX'.join(result)

x_args2cmd__mutmut_mutants : ClassVar[MutantDict] = {
'x_args2cmd__mutmut_1': x_args2cmd__mutmut_1, 
    'x_args2cmd__mutmut_2': x_args2cmd__mutmut_2, 
    'x_args2cmd__mutmut_3': x_args2cmd__mutmut_3, 
    'x_args2cmd__mutmut_4': x_args2cmd__mutmut_4, 
    'x_args2cmd__mutmut_5': x_args2cmd__mutmut_5, 
    'x_args2cmd__mutmut_6': x_args2cmd__mutmut_6, 
    'x_args2cmd__mutmut_7': x_args2cmd__mutmut_7, 
    'x_args2cmd__mutmut_8': x_args2cmd__mutmut_8, 
    'x_args2cmd__mutmut_9': x_args2cmd__mutmut_9, 
    'x_args2cmd__mutmut_10': x_args2cmd__mutmut_10, 
    'x_args2cmd__mutmut_11': x_args2cmd__mutmut_11, 
    'x_args2cmd__mutmut_12': x_args2cmd__mutmut_12, 
    'x_args2cmd__mutmut_13': x_args2cmd__mutmut_13, 
    'x_args2cmd__mutmut_14': x_args2cmd__mutmut_14, 
    'x_args2cmd__mutmut_15': x_args2cmd__mutmut_15, 
    'x_args2cmd__mutmut_16': x_args2cmd__mutmut_16, 
    'x_args2cmd__mutmut_17': x_args2cmd__mutmut_17, 
    'x_args2cmd__mutmut_18': x_args2cmd__mutmut_18, 
    'x_args2cmd__mutmut_19': x_args2cmd__mutmut_19, 
    'x_args2cmd__mutmut_20': x_args2cmd__mutmut_20, 
    'x_args2cmd__mutmut_21': x_args2cmd__mutmut_21, 
    'x_args2cmd__mutmut_22': x_args2cmd__mutmut_22, 
    'x_args2cmd__mutmut_23': x_args2cmd__mutmut_23, 
    'x_args2cmd__mutmut_24': x_args2cmd__mutmut_24, 
    'x_args2cmd__mutmut_25': x_args2cmd__mutmut_25, 
    'x_args2cmd__mutmut_26': x_args2cmd__mutmut_26, 
    'x_args2cmd__mutmut_27': x_args2cmd__mutmut_27, 
    'x_args2cmd__mutmut_28': x_args2cmd__mutmut_28, 
    'x_args2cmd__mutmut_29': x_args2cmd__mutmut_29, 
    'x_args2cmd__mutmut_30': x_args2cmd__mutmut_30, 
    'x_args2cmd__mutmut_31': x_args2cmd__mutmut_31, 
    'x_args2cmd__mutmut_32': x_args2cmd__mutmut_32, 
    'x_args2cmd__mutmut_33': x_args2cmd__mutmut_33, 
    'x_args2cmd__mutmut_34': x_args2cmd__mutmut_34, 
    'x_args2cmd__mutmut_35': x_args2cmd__mutmut_35, 
    'x_args2cmd__mutmut_36': x_args2cmd__mutmut_36, 
    'x_args2cmd__mutmut_37': x_args2cmd__mutmut_37, 
    'x_args2cmd__mutmut_38': x_args2cmd__mutmut_38, 
    'x_args2cmd__mutmut_39': x_args2cmd__mutmut_39
}

def args2cmd(*args, **kwargs):
    result = _mutmut_trampoline(x_args2cmd__mutmut_orig, x_args2cmd__mutmut_mutants, args, kwargs)
    return result 

args2cmd.__signature__ = _mutmut_signature(x_args2cmd__mutmut_orig)
x_args2cmd__mutmut_orig.__name__ = 'x_args2cmd'


def x_parse_int_list__mutmut_orig(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_1(range_string, delim='XX,XX', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_2(range_string, delim=',', range_delim='XX-XX'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_3(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = None

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_4(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(None):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_5(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim not in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_6(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = None
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_7(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(None)
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_8(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(None, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_9(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, None))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_10(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_11(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, ))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_12(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(None)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_13(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output = list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_14(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output -= list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_15(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(None)

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_16(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(None, max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_17(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), None))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_18(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_19(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), ))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_20(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(None), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_21(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits) - 1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_22(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(None)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_23(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+2))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_24(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_25(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            break

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def x_parse_int_list__mutmut_26(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(None)

    return sorted(output)


def x_parse_int_list__mutmut_27(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(None))

    return sorted(output)


def x_parse_int_list__mutmut_28(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(None)

x_parse_int_list__mutmut_mutants : ClassVar[MutantDict] = {
'x_parse_int_list__mutmut_1': x_parse_int_list__mutmut_1, 
    'x_parse_int_list__mutmut_2': x_parse_int_list__mutmut_2, 
    'x_parse_int_list__mutmut_3': x_parse_int_list__mutmut_3, 
    'x_parse_int_list__mutmut_4': x_parse_int_list__mutmut_4, 
    'x_parse_int_list__mutmut_5': x_parse_int_list__mutmut_5, 
    'x_parse_int_list__mutmut_6': x_parse_int_list__mutmut_6, 
    'x_parse_int_list__mutmut_7': x_parse_int_list__mutmut_7, 
    'x_parse_int_list__mutmut_8': x_parse_int_list__mutmut_8, 
    'x_parse_int_list__mutmut_9': x_parse_int_list__mutmut_9, 
    'x_parse_int_list__mutmut_10': x_parse_int_list__mutmut_10, 
    'x_parse_int_list__mutmut_11': x_parse_int_list__mutmut_11, 
    'x_parse_int_list__mutmut_12': x_parse_int_list__mutmut_12, 
    'x_parse_int_list__mutmut_13': x_parse_int_list__mutmut_13, 
    'x_parse_int_list__mutmut_14': x_parse_int_list__mutmut_14, 
    'x_parse_int_list__mutmut_15': x_parse_int_list__mutmut_15, 
    'x_parse_int_list__mutmut_16': x_parse_int_list__mutmut_16, 
    'x_parse_int_list__mutmut_17': x_parse_int_list__mutmut_17, 
    'x_parse_int_list__mutmut_18': x_parse_int_list__mutmut_18, 
    'x_parse_int_list__mutmut_19': x_parse_int_list__mutmut_19, 
    'x_parse_int_list__mutmut_20': x_parse_int_list__mutmut_20, 
    'x_parse_int_list__mutmut_21': x_parse_int_list__mutmut_21, 
    'x_parse_int_list__mutmut_22': x_parse_int_list__mutmut_22, 
    'x_parse_int_list__mutmut_23': x_parse_int_list__mutmut_23, 
    'x_parse_int_list__mutmut_24': x_parse_int_list__mutmut_24, 
    'x_parse_int_list__mutmut_25': x_parse_int_list__mutmut_25, 
    'x_parse_int_list__mutmut_26': x_parse_int_list__mutmut_26, 
    'x_parse_int_list__mutmut_27': x_parse_int_list__mutmut_27, 
    'x_parse_int_list__mutmut_28': x_parse_int_list__mutmut_28
}

def parse_int_list(*args, **kwargs):
    result = _mutmut_trampoline(x_parse_int_list__mutmut_orig, x_parse_int_list__mutmut_mutants, args, kwargs)
    return result 

parse_int_list.__signature__ = _mutmut_signature(x_parse_int_list__mutmut_orig)
x_parse_int_list__mutmut_orig.__name__ = 'x_parse_int_list'


def x_format_int_list__mutmut_orig(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_1(int_list, delim='XX,XX', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_2(int_list, delim=',', range_delim='XX-XX', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_3(int_list, delim=',', range_delim='-', delim_space=True):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_4(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = None
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_5(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = None

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_6(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(None):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_7(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) <= 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_8(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 2:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_9(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(None)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_10(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) >= 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_11(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 2:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_12(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = None

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_13(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x + contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_14(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[+1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_15(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-2]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_16(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta != 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_17(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 2:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_18(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(None)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_19(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta >= 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_20(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 2:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_21(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = None
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_22(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(None,
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_23(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      None,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_24(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      None)
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_25(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_26(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_27(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      )
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_28(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = 'XX{:d}{}{:d}XX'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_29(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:D}{}{:D}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_30(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(None),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_31(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(None))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_32(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(None)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_33(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(None)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_34(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                break

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_35(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = None

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_36(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x + contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_37(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_38(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta != 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_39(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 2:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_40(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(None)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_41(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta >= 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_42(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 2:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_43(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(None)
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_44(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(None)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_45(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                break

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_46(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) != 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_47(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 2:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_48(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(None)
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_49(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) >= 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_50(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 2:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_51(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = None
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_52(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(None,
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_53(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  None,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_54(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  None)
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_55(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_56(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_57(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  )
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_58(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = 'XX{:d}{}{:d}XX'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_59(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:D}{}{:D}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_60(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(None),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_61(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(None))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_62(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(None)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_63(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = None
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_64(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(None)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_65(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim - ' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_66(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+'XX XX').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def x_format_int_list__mutmut_67(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = None

    return output_str


def x_format_int_list__mutmut_68(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(None)

    return output_str

x_format_int_list__mutmut_mutants : ClassVar[MutantDict] = {
'x_format_int_list__mutmut_1': x_format_int_list__mutmut_1, 
    'x_format_int_list__mutmut_2': x_format_int_list__mutmut_2, 
    'x_format_int_list__mutmut_3': x_format_int_list__mutmut_3, 
    'x_format_int_list__mutmut_4': x_format_int_list__mutmut_4, 
    'x_format_int_list__mutmut_5': x_format_int_list__mutmut_5, 
    'x_format_int_list__mutmut_6': x_format_int_list__mutmut_6, 
    'x_format_int_list__mutmut_7': x_format_int_list__mutmut_7, 
    'x_format_int_list__mutmut_8': x_format_int_list__mutmut_8, 
    'x_format_int_list__mutmut_9': x_format_int_list__mutmut_9, 
    'x_format_int_list__mutmut_10': x_format_int_list__mutmut_10, 
    'x_format_int_list__mutmut_11': x_format_int_list__mutmut_11, 
    'x_format_int_list__mutmut_12': x_format_int_list__mutmut_12, 
    'x_format_int_list__mutmut_13': x_format_int_list__mutmut_13, 
    'x_format_int_list__mutmut_14': x_format_int_list__mutmut_14, 
    'x_format_int_list__mutmut_15': x_format_int_list__mutmut_15, 
    'x_format_int_list__mutmut_16': x_format_int_list__mutmut_16, 
    'x_format_int_list__mutmut_17': x_format_int_list__mutmut_17, 
    'x_format_int_list__mutmut_18': x_format_int_list__mutmut_18, 
    'x_format_int_list__mutmut_19': x_format_int_list__mutmut_19, 
    'x_format_int_list__mutmut_20': x_format_int_list__mutmut_20, 
    'x_format_int_list__mutmut_21': x_format_int_list__mutmut_21, 
    'x_format_int_list__mutmut_22': x_format_int_list__mutmut_22, 
    'x_format_int_list__mutmut_23': x_format_int_list__mutmut_23, 
    'x_format_int_list__mutmut_24': x_format_int_list__mutmut_24, 
    'x_format_int_list__mutmut_25': x_format_int_list__mutmut_25, 
    'x_format_int_list__mutmut_26': x_format_int_list__mutmut_26, 
    'x_format_int_list__mutmut_27': x_format_int_list__mutmut_27, 
    'x_format_int_list__mutmut_28': x_format_int_list__mutmut_28, 
    'x_format_int_list__mutmut_29': x_format_int_list__mutmut_29, 
    'x_format_int_list__mutmut_30': x_format_int_list__mutmut_30, 
    'x_format_int_list__mutmut_31': x_format_int_list__mutmut_31, 
    'x_format_int_list__mutmut_32': x_format_int_list__mutmut_32, 
    'x_format_int_list__mutmut_33': x_format_int_list__mutmut_33, 
    'x_format_int_list__mutmut_34': x_format_int_list__mutmut_34, 
    'x_format_int_list__mutmut_35': x_format_int_list__mutmut_35, 
    'x_format_int_list__mutmut_36': x_format_int_list__mutmut_36, 
    'x_format_int_list__mutmut_37': x_format_int_list__mutmut_37, 
    'x_format_int_list__mutmut_38': x_format_int_list__mutmut_38, 
    'x_format_int_list__mutmut_39': x_format_int_list__mutmut_39, 
    'x_format_int_list__mutmut_40': x_format_int_list__mutmut_40, 
    'x_format_int_list__mutmut_41': x_format_int_list__mutmut_41, 
    'x_format_int_list__mutmut_42': x_format_int_list__mutmut_42, 
    'x_format_int_list__mutmut_43': x_format_int_list__mutmut_43, 
    'x_format_int_list__mutmut_44': x_format_int_list__mutmut_44, 
    'x_format_int_list__mutmut_45': x_format_int_list__mutmut_45, 
    'x_format_int_list__mutmut_46': x_format_int_list__mutmut_46, 
    'x_format_int_list__mutmut_47': x_format_int_list__mutmut_47, 
    'x_format_int_list__mutmut_48': x_format_int_list__mutmut_48, 
    'x_format_int_list__mutmut_49': x_format_int_list__mutmut_49, 
    'x_format_int_list__mutmut_50': x_format_int_list__mutmut_50, 
    'x_format_int_list__mutmut_51': x_format_int_list__mutmut_51, 
    'x_format_int_list__mutmut_52': x_format_int_list__mutmut_52, 
    'x_format_int_list__mutmut_53': x_format_int_list__mutmut_53, 
    'x_format_int_list__mutmut_54': x_format_int_list__mutmut_54, 
    'x_format_int_list__mutmut_55': x_format_int_list__mutmut_55, 
    'x_format_int_list__mutmut_56': x_format_int_list__mutmut_56, 
    'x_format_int_list__mutmut_57': x_format_int_list__mutmut_57, 
    'x_format_int_list__mutmut_58': x_format_int_list__mutmut_58, 
    'x_format_int_list__mutmut_59': x_format_int_list__mutmut_59, 
    'x_format_int_list__mutmut_60': x_format_int_list__mutmut_60, 
    'x_format_int_list__mutmut_61': x_format_int_list__mutmut_61, 
    'x_format_int_list__mutmut_62': x_format_int_list__mutmut_62, 
    'x_format_int_list__mutmut_63': x_format_int_list__mutmut_63, 
    'x_format_int_list__mutmut_64': x_format_int_list__mutmut_64, 
    'x_format_int_list__mutmut_65': x_format_int_list__mutmut_65, 
    'x_format_int_list__mutmut_66': x_format_int_list__mutmut_66, 
    'x_format_int_list__mutmut_67': x_format_int_list__mutmut_67, 
    'x_format_int_list__mutmut_68': x_format_int_list__mutmut_68
}

def format_int_list(*args, **kwargs):
    result = _mutmut_trampoline(x_format_int_list__mutmut_orig, x_format_int_list__mutmut_mutants, args, kwargs)
    return result 

format_int_list.__signature__ = _mutmut_signature(x_format_int_list__mutmut_orig)
x_format_int_list__mutmut_orig.__name__ = 'x_format_int_list'


def x_complement_int_list__mutmut_orig(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_1(
        range_string, range_start=1, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_2(
        range_string, range_start=0, range_end=None,
        delim='XX,XX', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_3(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='XX-XX'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_4(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = None
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_5(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(None)
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_6(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(None, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_7(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, None, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_8(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, None))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_9(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_10(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_11(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, ))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_12(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is not None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_13(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = None
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_14(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) - 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_15(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(None) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_16(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 2
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_17(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = None
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_18(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = None
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_19(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list + set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_20(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) + int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_21(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        None) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_22(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(None)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_23(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(None)
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_24(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(None))
    return format_int_list(complement_values, delim, range_delim)


def x_complement_int_list__mutmut_25(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(None, delim, range_delim)


def x_complement_int_list__mutmut_26(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, None, range_delim)


def x_complement_int_list__mutmut_27(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, None)


def x_complement_int_list__mutmut_28(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(delim, range_delim)


def x_complement_int_list__mutmut_29(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, range_delim)


def x_complement_int_list__mutmut_30(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, )

x_complement_int_list__mutmut_mutants : ClassVar[MutantDict] = {
'x_complement_int_list__mutmut_1': x_complement_int_list__mutmut_1, 
    'x_complement_int_list__mutmut_2': x_complement_int_list__mutmut_2, 
    'x_complement_int_list__mutmut_3': x_complement_int_list__mutmut_3, 
    'x_complement_int_list__mutmut_4': x_complement_int_list__mutmut_4, 
    'x_complement_int_list__mutmut_5': x_complement_int_list__mutmut_5, 
    'x_complement_int_list__mutmut_6': x_complement_int_list__mutmut_6, 
    'x_complement_int_list__mutmut_7': x_complement_int_list__mutmut_7, 
    'x_complement_int_list__mutmut_8': x_complement_int_list__mutmut_8, 
    'x_complement_int_list__mutmut_9': x_complement_int_list__mutmut_9, 
    'x_complement_int_list__mutmut_10': x_complement_int_list__mutmut_10, 
    'x_complement_int_list__mutmut_11': x_complement_int_list__mutmut_11, 
    'x_complement_int_list__mutmut_12': x_complement_int_list__mutmut_12, 
    'x_complement_int_list__mutmut_13': x_complement_int_list__mutmut_13, 
    'x_complement_int_list__mutmut_14': x_complement_int_list__mutmut_14, 
    'x_complement_int_list__mutmut_15': x_complement_int_list__mutmut_15, 
    'x_complement_int_list__mutmut_16': x_complement_int_list__mutmut_16, 
    'x_complement_int_list__mutmut_17': x_complement_int_list__mutmut_17, 
    'x_complement_int_list__mutmut_18': x_complement_int_list__mutmut_18, 
    'x_complement_int_list__mutmut_19': x_complement_int_list__mutmut_19, 
    'x_complement_int_list__mutmut_20': x_complement_int_list__mutmut_20, 
    'x_complement_int_list__mutmut_21': x_complement_int_list__mutmut_21, 
    'x_complement_int_list__mutmut_22': x_complement_int_list__mutmut_22, 
    'x_complement_int_list__mutmut_23': x_complement_int_list__mutmut_23, 
    'x_complement_int_list__mutmut_24': x_complement_int_list__mutmut_24, 
    'x_complement_int_list__mutmut_25': x_complement_int_list__mutmut_25, 
    'x_complement_int_list__mutmut_26': x_complement_int_list__mutmut_26, 
    'x_complement_int_list__mutmut_27': x_complement_int_list__mutmut_27, 
    'x_complement_int_list__mutmut_28': x_complement_int_list__mutmut_28, 
    'x_complement_int_list__mutmut_29': x_complement_int_list__mutmut_29, 
    'x_complement_int_list__mutmut_30': x_complement_int_list__mutmut_30
}

def complement_int_list(*args, **kwargs):
    result = _mutmut_trampoline(x_complement_int_list__mutmut_orig, x_complement_int_list__mutmut_mutants, args, kwargs)
    return result 

complement_int_list.__signature__ = _mutmut_signature(x_complement_int_list__mutmut_orig)
x_complement_int_list__mutmut_orig.__name__ = 'x_complement_int_list'


def x_int_ranges_from_int_list__mutmut_orig(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_1(range_string, delim='XX,XX', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_2(range_string, delim=',', range_delim='XX-XX'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_3(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = None
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_4(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = None
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_5(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        None)
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_6(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(None, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_7(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, None, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_8(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, None))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_9(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_10(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_11(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, ))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_12(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(None):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_13(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split('XX,XX'):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_14(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if 'XX-XX' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_15(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' not in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_16(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = None
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_17(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split(None)
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_18(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('XX-XX')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_19(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = None
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_20(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append(None)
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_21(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(None), int(end)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_22(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(None)))
    return tuple(int_tuples)


def x_int_ranges_from_int_list__mutmut_23(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(None)

x_int_ranges_from_int_list__mutmut_mutants : ClassVar[MutantDict] = {
'x_int_ranges_from_int_list__mutmut_1': x_int_ranges_from_int_list__mutmut_1, 
    'x_int_ranges_from_int_list__mutmut_2': x_int_ranges_from_int_list__mutmut_2, 
    'x_int_ranges_from_int_list__mutmut_3': x_int_ranges_from_int_list__mutmut_3, 
    'x_int_ranges_from_int_list__mutmut_4': x_int_ranges_from_int_list__mutmut_4, 
    'x_int_ranges_from_int_list__mutmut_5': x_int_ranges_from_int_list__mutmut_5, 
    'x_int_ranges_from_int_list__mutmut_6': x_int_ranges_from_int_list__mutmut_6, 
    'x_int_ranges_from_int_list__mutmut_7': x_int_ranges_from_int_list__mutmut_7, 
    'x_int_ranges_from_int_list__mutmut_8': x_int_ranges_from_int_list__mutmut_8, 
    'x_int_ranges_from_int_list__mutmut_9': x_int_ranges_from_int_list__mutmut_9, 
    'x_int_ranges_from_int_list__mutmut_10': x_int_ranges_from_int_list__mutmut_10, 
    'x_int_ranges_from_int_list__mutmut_11': x_int_ranges_from_int_list__mutmut_11, 
    'x_int_ranges_from_int_list__mutmut_12': x_int_ranges_from_int_list__mutmut_12, 
    'x_int_ranges_from_int_list__mutmut_13': x_int_ranges_from_int_list__mutmut_13, 
    'x_int_ranges_from_int_list__mutmut_14': x_int_ranges_from_int_list__mutmut_14, 
    'x_int_ranges_from_int_list__mutmut_15': x_int_ranges_from_int_list__mutmut_15, 
    'x_int_ranges_from_int_list__mutmut_16': x_int_ranges_from_int_list__mutmut_16, 
    'x_int_ranges_from_int_list__mutmut_17': x_int_ranges_from_int_list__mutmut_17, 
    'x_int_ranges_from_int_list__mutmut_18': x_int_ranges_from_int_list__mutmut_18, 
    'x_int_ranges_from_int_list__mutmut_19': x_int_ranges_from_int_list__mutmut_19, 
    'x_int_ranges_from_int_list__mutmut_20': x_int_ranges_from_int_list__mutmut_20, 
    'x_int_ranges_from_int_list__mutmut_21': x_int_ranges_from_int_list__mutmut_21, 
    'x_int_ranges_from_int_list__mutmut_22': x_int_ranges_from_int_list__mutmut_22, 
    'x_int_ranges_from_int_list__mutmut_23': x_int_ranges_from_int_list__mutmut_23
}

def int_ranges_from_int_list(*args, **kwargs):
    result = _mutmut_trampoline(x_int_ranges_from_int_list__mutmut_orig, x_int_ranges_from_int_list__mutmut_mutants, args, kwargs)
    return result 

int_ranges_from_int_list.__signature__ = _mutmut_signature(x_int_ranges_from_int_list__mutmut_orig)
x_int_ranges_from_int_list__mutmut_orig.__name__ = 'x_int_ranges_from_int_list'


class MultiReplace:
    """
    MultiReplace is a tool for doing multiple find/replace actions in one pass.

    Given a mapping of values to be replaced it allows for all of the matching
    values to be replaced in a single pass which can save a lot of performance
    on very large strings. In addition to simple replace, it also allows for
    replacing based on regular expressions.

    Keyword Arguments:

    :type regex: bool
    :param regex: Treat search keys as regular expressions [Default: False]
    :type flags: int
    :param flags: flags to pass to the regex engine during compile

    Dictionary Usage::

        from boltons import strutils
        s = strutils.MultiReplace({
            'foo': 'zoo',
            'cat': 'hat',
            'bat': 'kraken'
        })
        new = s.sub('The foo bar cat ate a bat')
        new == 'The zoo bar hat ate a kraken'

    Iterable Usage::

        from boltons import strutils
        s = strutils.MultiReplace([
            ('foo', 'zoo'),
            ('cat', 'hat'),
            ('bat', 'kraken)'
        ])
        new = s.sub('The foo bar cat ate a bat')
        new == 'The zoo bar hat ate a kraken'


    The constructor can be passed a dictionary or other mapping as well as
    an iterable of tuples. If given an iterable, the substitution will be run
    in the order the replacement values are specified in the iterable. This is
    also true if it is given an OrderedDict. If given a dictionary then the
    order will be non-deterministic::

        >>> 'foo bar baz'.replace('foo', 'baz').replace('baz', 'bar')
        'bar bar bar'
        >>> m = MultiReplace({'foo': 'baz', 'baz': 'bar'})
        >>> m.sub('foo bar baz')
        'baz bar bar'

    This is because the order of replacement can matter if you're inserting
    something that might be replaced by a later substitution. Pay attention and
    if you need to rely on order then consider using a list of tuples instead
    of a dictionary.
    """

    def xǁMultiReplaceǁ__init____mutmut_orig(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_1(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = None
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_2(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'XXregexXX': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_3(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'REGEX': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_4(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': True,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_5(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'XXflagsXX': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_6(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'FLAGS': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_7(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 1,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_8(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(None)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_9(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = None
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_10(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = None

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_11(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = None

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_12(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(None):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_13(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = None
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_14(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_15(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['XXregexXX']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_16(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['REGEX']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_17(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = None
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_18(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(None)
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_19(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[1])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_20(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = None
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_21(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[1]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_22(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = None

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_23(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[1].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_24(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(None)
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_25(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = None

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_26(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[2]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_27(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = None

    def xǁMultiReplaceǁ__init____mutmut_28(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            None,
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_29(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=None
        )

    def xǁMultiReplaceǁ__init____mutmut_30(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_31(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            )

    def xǁMultiReplaceǁ__init____mutmut_32(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(None),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_33(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            'XX|XX'.join(regex_values),
            flags=options['flags']
        )

    def xǁMultiReplaceǁ__init____mutmut_34(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['XXflagsXX']
        )

    def xǁMultiReplaceǁ__init____mutmut_35(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['FLAGS']
        )
    
    xǁMultiReplaceǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiReplaceǁ__init____mutmut_1': xǁMultiReplaceǁ__init____mutmut_1, 
        'xǁMultiReplaceǁ__init____mutmut_2': xǁMultiReplaceǁ__init____mutmut_2, 
        'xǁMultiReplaceǁ__init____mutmut_3': xǁMultiReplaceǁ__init____mutmut_3, 
        'xǁMultiReplaceǁ__init____mutmut_4': xǁMultiReplaceǁ__init____mutmut_4, 
        'xǁMultiReplaceǁ__init____mutmut_5': xǁMultiReplaceǁ__init____mutmut_5, 
        'xǁMultiReplaceǁ__init____mutmut_6': xǁMultiReplaceǁ__init____mutmut_6, 
        'xǁMultiReplaceǁ__init____mutmut_7': xǁMultiReplaceǁ__init____mutmut_7, 
        'xǁMultiReplaceǁ__init____mutmut_8': xǁMultiReplaceǁ__init____mutmut_8, 
        'xǁMultiReplaceǁ__init____mutmut_9': xǁMultiReplaceǁ__init____mutmut_9, 
        'xǁMultiReplaceǁ__init____mutmut_10': xǁMultiReplaceǁ__init____mutmut_10, 
        'xǁMultiReplaceǁ__init____mutmut_11': xǁMultiReplaceǁ__init____mutmut_11, 
        'xǁMultiReplaceǁ__init____mutmut_12': xǁMultiReplaceǁ__init____mutmut_12, 
        'xǁMultiReplaceǁ__init____mutmut_13': xǁMultiReplaceǁ__init____mutmut_13, 
        'xǁMultiReplaceǁ__init____mutmut_14': xǁMultiReplaceǁ__init____mutmut_14, 
        'xǁMultiReplaceǁ__init____mutmut_15': xǁMultiReplaceǁ__init____mutmut_15, 
        'xǁMultiReplaceǁ__init____mutmut_16': xǁMultiReplaceǁ__init____mutmut_16, 
        'xǁMultiReplaceǁ__init____mutmut_17': xǁMultiReplaceǁ__init____mutmut_17, 
        'xǁMultiReplaceǁ__init____mutmut_18': xǁMultiReplaceǁ__init____mutmut_18, 
        'xǁMultiReplaceǁ__init____mutmut_19': xǁMultiReplaceǁ__init____mutmut_19, 
        'xǁMultiReplaceǁ__init____mutmut_20': xǁMultiReplaceǁ__init____mutmut_20, 
        'xǁMultiReplaceǁ__init____mutmut_21': xǁMultiReplaceǁ__init____mutmut_21, 
        'xǁMultiReplaceǁ__init____mutmut_22': xǁMultiReplaceǁ__init____mutmut_22, 
        'xǁMultiReplaceǁ__init____mutmut_23': xǁMultiReplaceǁ__init____mutmut_23, 
        'xǁMultiReplaceǁ__init____mutmut_24': xǁMultiReplaceǁ__init____mutmut_24, 
        'xǁMultiReplaceǁ__init____mutmut_25': xǁMultiReplaceǁ__init____mutmut_25, 
        'xǁMultiReplaceǁ__init____mutmut_26': xǁMultiReplaceǁ__init____mutmut_26, 
        'xǁMultiReplaceǁ__init____mutmut_27': xǁMultiReplaceǁ__init____mutmut_27, 
        'xǁMultiReplaceǁ__init____mutmut_28': xǁMultiReplaceǁ__init____mutmut_28, 
        'xǁMultiReplaceǁ__init____mutmut_29': xǁMultiReplaceǁ__init____mutmut_29, 
        'xǁMultiReplaceǁ__init____mutmut_30': xǁMultiReplaceǁ__init____mutmut_30, 
        'xǁMultiReplaceǁ__init____mutmut_31': xǁMultiReplaceǁ__init____mutmut_31, 
        'xǁMultiReplaceǁ__init____mutmut_32': xǁMultiReplaceǁ__init____mutmut_32, 
        'xǁMultiReplaceǁ__init____mutmut_33': xǁMultiReplaceǁ__init____mutmut_33, 
        'xǁMultiReplaceǁ__init____mutmut_34': xǁMultiReplaceǁ__init____mutmut_34, 
        'xǁMultiReplaceǁ__init____mutmut_35': xǁMultiReplaceǁ__init____mutmut_35
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiReplaceǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMultiReplaceǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMultiReplaceǁ__init____mutmut_orig)
    xǁMultiReplaceǁ__init____mutmut_orig.__name__ = 'xǁMultiReplaceǁ__init__'

    def xǁMultiReplaceǁ_get_value__mutmut_orig(self, match):
        """Given a match object find replacement value."""
        group_dict = match.groupdict()
        key = [x for x in group_dict if group_dict[x]][0]
        return self.group_map[key]

    def xǁMultiReplaceǁ_get_value__mutmut_1(self, match):
        """Given a match object find replacement value."""
        group_dict = None
        key = [x for x in group_dict if group_dict[x]][0]
        return self.group_map[key]

    def xǁMultiReplaceǁ_get_value__mutmut_2(self, match):
        """Given a match object find replacement value."""
        group_dict = match.groupdict()
        key = None
        return self.group_map[key]

    def xǁMultiReplaceǁ_get_value__mutmut_3(self, match):
        """Given a match object find replacement value."""
        group_dict = match.groupdict()
        key = [x for x in group_dict if group_dict[x]][1]
        return self.group_map[key]
    
    xǁMultiReplaceǁ_get_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiReplaceǁ_get_value__mutmut_1': xǁMultiReplaceǁ_get_value__mutmut_1, 
        'xǁMultiReplaceǁ_get_value__mutmut_2': xǁMultiReplaceǁ_get_value__mutmut_2, 
        'xǁMultiReplaceǁ_get_value__mutmut_3': xǁMultiReplaceǁ_get_value__mutmut_3
    }
    
    def _get_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiReplaceǁ_get_value__mutmut_orig"), object.__getattribute__(self, "xǁMultiReplaceǁ_get_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_value.__signature__ = _mutmut_signature(xǁMultiReplaceǁ_get_value__mutmut_orig)
    xǁMultiReplaceǁ_get_value__mutmut_orig.__name__ = 'xǁMultiReplaceǁ_get_value'

    def xǁMultiReplaceǁsub__mutmut_orig(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(self._get_value, text)

    def xǁMultiReplaceǁsub__mutmut_1(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(None, text)

    def xǁMultiReplaceǁsub__mutmut_2(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(self._get_value, None)

    def xǁMultiReplaceǁsub__mutmut_3(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(text)

    def xǁMultiReplaceǁsub__mutmut_4(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(self._get_value, )
    
    xǁMultiReplaceǁsub__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiReplaceǁsub__mutmut_1': xǁMultiReplaceǁsub__mutmut_1, 
        'xǁMultiReplaceǁsub__mutmut_2': xǁMultiReplaceǁsub__mutmut_2, 
        'xǁMultiReplaceǁsub__mutmut_3': xǁMultiReplaceǁsub__mutmut_3, 
        'xǁMultiReplaceǁsub__mutmut_4': xǁMultiReplaceǁsub__mutmut_4
    }
    
    def sub(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiReplaceǁsub__mutmut_orig"), object.__getattribute__(self, "xǁMultiReplaceǁsub__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sub.__signature__ = _mutmut_signature(xǁMultiReplaceǁsub__mutmut_orig)
    xǁMultiReplaceǁsub__mutmut_orig.__name__ = 'xǁMultiReplaceǁsub'


def x_multi_replace__mutmut_orig(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(sub_map, **kwargs)
    return m.sub(text)


def x_multi_replace__mutmut_1(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = None
    return m.sub(text)


def x_multi_replace__mutmut_2(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(None, **kwargs)
    return m.sub(text)


def x_multi_replace__mutmut_3(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(**kwargs)
    return m.sub(text)


def x_multi_replace__mutmut_4(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(sub_map, )
    return m.sub(text)


def x_multi_replace__mutmut_5(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(sub_map, **kwargs)
    return m.sub(None)

x_multi_replace__mutmut_mutants : ClassVar[MutantDict] = {
'x_multi_replace__mutmut_1': x_multi_replace__mutmut_1, 
    'x_multi_replace__mutmut_2': x_multi_replace__mutmut_2, 
    'x_multi_replace__mutmut_3': x_multi_replace__mutmut_3, 
    'x_multi_replace__mutmut_4': x_multi_replace__mutmut_4, 
    'x_multi_replace__mutmut_5': x_multi_replace__mutmut_5
}

def multi_replace(*args, **kwargs):
    result = _mutmut_trampoline(x_multi_replace__mutmut_orig, x_multi_replace__mutmut_mutants, args, kwargs)
    return result 

multi_replace.__signature__ = _mutmut_signature(x_multi_replace__mutmut_orig)
x_multi_replace__mutmut_orig.__name__ = 'x_multi_replace'


def x_unwrap_text__mutmut_orig(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_1(text, ending='XX\n\nXX'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_2(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = None
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_3(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = None
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_4(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = None
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_5(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(None)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_6(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(None)
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_7(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(None))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_8(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append('XX XX'.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_9(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = None
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_10(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(None)
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_11(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(None))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_12(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append('XX XX'.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_13(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is not None:
        return all_grafs
    return ending.join(all_grafs)


def x_unwrap_text__mutmut_14(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(None)

x_unwrap_text__mutmut_mutants : ClassVar[MutantDict] = {
'x_unwrap_text__mutmut_1': x_unwrap_text__mutmut_1, 
    'x_unwrap_text__mutmut_2': x_unwrap_text__mutmut_2, 
    'x_unwrap_text__mutmut_3': x_unwrap_text__mutmut_3, 
    'x_unwrap_text__mutmut_4': x_unwrap_text__mutmut_4, 
    'x_unwrap_text__mutmut_5': x_unwrap_text__mutmut_5, 
    'x_unwrap_text__mutmut_6': x_unwrap_text__mutmut_6, 
    'x_unwrap_text__mutmut_7': x_unwrap_text__mutmut_7, 
    'x_unwrap_text__mutmut_8': x_unwrap_text__mutmut_8, 
    'x_unwrap_text__mutmut_9': x_unwrap_text__mutmut_9, 
    'x_unwrap_text__mutmut_10': x_unwrap_text__mutmut_10, 
    'x_unwrap_text__mutmut_11': x_unwrap_text__mutmut_11, 
    'x_unwrap_text__mutmut_12': x_unwrap_text__mutmut_12, 
    'x_unwrap_text__mutmut_13': x_unwrap_text__mutmut_13, 
    'x_unwrap_text__mutmut_14': x_unwrap_text__mutmut_14
}

def unwrap_text(*args, **kwargs):
    result = _mutmut_trampoline(x_unwrap_text__mutmut_orig, x_unwrap_text__mutmut_mutants, args, kwargs)
    return result 

unwrap_text.__signature__ = _mutmut_signature(x_unwrap_text__mutmut_orig)
x_unwrap_text__mutmut_orig.__name__ = 'x_unwrap_text'

def x_removeprefix__mutmut_orig(text: str, prefix: str) -> str:
    r"""
    Remove `prefix` from start of `text` if present.

    Backport of `str.removeprefix` for Python versions less than 3.9.

    Args:
        text: A string to remove the prefix from.
        prefix: The string to remove from the beginning of `text`.
    """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def x_removeprefix__mutmut_1(text: str, prefix: str) -> str:
    r"""
    Remove `prefix` from start of `text` if present.

    Backport of `str.removeprefix` for Python versions less than 3.9.

    Args:
        text: A string to remove the prefix from.
        prefix: The string to remove from the beginning of `text`.
    """
    if text.startswith(None):
        return text[len(prefix):]
    return text

x_removeprefix__mutmut_mutants : ClassVar[MutantDict] = {
'x_removeprefix__mutmut_1': x_removeprefix__mutmut_1
}

def removeprefix(*args, **kwargs):
    result = _mutmut_trampoline(x_removeprefix__mutmut_orig, x_removeprefix__mutmut_mutants, args, kwargs)
    return result 

removeprefix.__signature__ = _mutmut_signature(x_removeprefix__mutmut_orig)
x_removeprefix__mutmut_orig.__name__ = 'x_removeprefix'
