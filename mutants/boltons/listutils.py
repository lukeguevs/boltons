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

"""Python's builtin :class:`list` is a very fast and efficient
sequence type, but it could be better for certain access patterns,
such as non-sequential insertion into a large lists. ``listutils``
provides a pure-Python solution to this problem.

For utilities for working with iterables and lists, check out
:mod:`iterutils`. For the a :class:`list`-based version of
:class:`collections.namedtuple`, check out :mod:`namedutils`.
"""


import operator
from math import log as math_log
from itertools import chain, islice

_MISSING = object()

# TODO: expose splaylist?
__all__ = ['BList', 'BarrelList']
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


# TODO: comparators
# TODO: keep track of list lengths and bisect to the right list for
# faster getitem (and slightly slower setitem and delitem ops)

class BarrelList(list):
    """The ``BarrelList`` is a :class:`list` subtype backed by many
    dynamically-scaled sublists, to provide better scaling and random
    insertion/deletion characteristics. It is a subtype of the builtin
    :class:`list` and has an identical API, supporting indexing,
    slicing, sorting, etc. If application requirements call for
    something more performant, consider the `blist module available on
    PyPI`_.

    The name comes by way of Kurt Rose, who said it reminded him of
    barrel shifters. Not sure how, but it's BList-like, so the name
    stuck. BList is of course a reference to `B-trees`_.

    Args:
        iterable: An optional iterable of initial values for the list.

    >>> blist = BList(range(100000))
    >>> blist.pop(50000)
    50000
    >>> len(blist)
    99999
    >>> len(blist.lists)  # how many underlying lists
    8
    >>> slice_idx = blist.lists[0][-1]
    >>> blist[slice_idx:slice_idx + 2]
    BarrelList([11637, 11638])

    Slicing is supported and works just fine across list borders,
    returning another instance of the BarrelList.

    .. _blist module available on PyPI: https://pypi.python.org/pypi/blist
    .. _B-trees: https://en.wikipedia.org/wiki/B-tree

    """

    _size_factor = 1520
    "This size factor is the result of tuning using the tune() function below."

    def xǁBarrelListǁ__init____mutmut_orig(self, iterable=None):
        self.lists = [[]]
        if iterable:
            self.extend(iterable)

    def xǁBarrelListǁ__init____mutmut_1(self, iterable=None):
        self.lists = None
        if iterable:
            self.extend(iterable)

    def xǁBarrelListǁ__init____mutmut_2(self, iterable=None):
        self.lists = [[]]
        if iterable:
            self.extend(None)
    
    xǁBarrelListǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__init____mutmut_1': xǁBarrelListǁ__init____mutmut_1, 
        'xǁBarrelListǁ__init____mutmut_2': xǁBarrelListǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBarrelListǁ__init____mutmut_orig)
    xǁBarrelListǁ__init____mutmut_orig.__name__ = 'xǁBarrelListǁ__init__'

    @property
    def _cur_size_limit(self):
        len_self, size_factor = len(self), self._size_factor
        return int(round(size_factor * math_log(len_self + 2, 2)))

    def xǁBarrelListǁ_translate_index__mutmut_orig(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_1(self, index):
        if index <= 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_2(self, index):
        if index < 1:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_3(self, index):
        if index < 0:
            index = len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_4(self, index):
        if index < 0:
            index -= len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_5(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = None
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_6(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(None):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_7(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = None
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_8(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx <= len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_9(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                return
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_10(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx = len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_11(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx += len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_12(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx <= 0:
            return None, None
        return list_idx, rel_idx

    def xǁBarrelListǁ_translate_index__mutmut_13(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 1:
            return None, None
        return list_idx, rel_idx
    
    xǁBarrelListǁ_translate_index__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ_translate_index__mutmut_1': xǁBarrelListǁ_translate_index__mutmut_1, 
        'xǁBarrelListǁ_translate_index__mutmut_2': xǁBarrelListǁ_translate_index__mutmut_2, 
        'xǁBarrelListǁ_translate_index__mutmut_3': xǁBarrelListǁ_translate_index__mutmut_3, 
        'xǁBarrelListǁ_translate_index__mutmut_4': xǁBarrelListǁ_translate_index__mutmut_4, 
        'xǁBarrelListǁ_translate_index__mutmut_5': xǁBarrelListǁ_translate_index__mutmut_5, 
        'xǁBarrelListǁ_translate_index__mutmut_6': xǁBarrelListǁ_translate_index__mutmut_6, 
        'xǁBarrelListǁ_translate_index__mutmut_7': xǁBarrelListǁ_translate_index__mutmut_7, 
        'xǁBarrelListǁ_translate_index__mutmut_8': xǁBarrelListǁ_translate_index__mutmut_8, 
        'xǁBarrelListǁ_translate_index__mutmut_9': xǁBarrelListǁ_translate_index__mutmut_9, 
        'xǁBarrelListǁ_translate_index__mutmut_10': xǁBarrelListǁ_translate_index__mutmut_10, 
        'xǁBarrelListǁ_translate_index__mutmut_11': xǁBarrelListǁ_translate_index__mutmut_11, 
        'xǁBarrelListǁ_translate_index__mutmut_12': xǁBarrelListǁ_translate_index__mutmut_12, 
        'xǁBarrelListǁ_translate_index__mutmut_13': xǁBarrelListǁ_translate_index__mutmut_13
    }
    
    def _translate_index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ_translate_index__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ_translate_index__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _translate_index.__signature__ = _mutmut_signature(xǁBarrelListǁ_translate_index__mutmut_orig)
    xǁBarrelListǁ_translate_index__mutmut_orig.__name__ = 'xǁBarrelListǁ_translate_index'

    def xǁBarrelListǁ_balance_list__mutmut_orig(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_1(self, list_idx):
        if list_idx <= 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_2(self, list_idx):
        if list_idx < 1:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_3(self, list_idx):
        if list_idx < 0:
            list_idx = len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_4(self, list_idx):
        if list_idx < 0:
            list_idx -= len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_5(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = None
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_6(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = None
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_7(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) >= size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_8(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = None
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_9(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit / 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_10(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 3
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_11(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) >= half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_12(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = None
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_13(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx - 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_14(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 2
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_15(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(None, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_16(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, None)
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_17(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_18(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, )
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_19(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[+half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_20(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[+half_limit:]
            return True
        return False

    def xǁBarrelListǁ_balance_list__mutmut_21(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return False
        return False

    def xǁBarrelListǁ_balance_list__mutmut_22(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return True
    
    xǁBarrelListǁ_balance_list__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ_balance_list__mutmut_1': xǁBarrelListǁ_balance_list__mutmut_1, 
        'xǁBarrelListǁ_balance_list__mutmut_2': xǁBarrelListǁ_balance_list__mutmut_2, 
        'xǁBarrelListǁ_balance_list__mutmut_3': xǁBarrelListǁ_balance_list__mutmut_3, 
        'xǁBarrelListǁ_balance_list__mutmut_4': xǁBarrelListǁ_balance_list__mutmut_4, 
        'xǁBarrelListǁ_balance_list__mutmut_5': xǁBarrelListǁ_balance_list__mutmut_5, 
        'xǁBarrelListǁ_balance_list__mutmut_6': xǁBarrelListǁ_balance_list__mutmut_6, 
        'xǁBarrelListǁ_balance_list__mutmut_7': xǁBarrelListǁ_balance_list__mutmut_7, 
        'xǁBarrelListǁ_balance_list__mutmut_8': xǁBarrelListǁ_balance_list__mutmut_8, 
        'xǁBarrelListǁ_balance_list__mutmut_9': xǁBarrelListǁ_balance_list__mutmut_9, 
        'xǁBarrelListǁ_balance_list__mutmut_10': xǁBarrelListǁ_balance_list__mutmut_10, 
        'xǁBarrelListǁ_balance_list__mutmut_11': xǁBarrelListǁ_balance_list__mutmut_11, 
        'xǁBarrelListǁ_balance_list__mutmut_12': xǁBarrelListǁ_balance_list__mutmut_12, 
        'xǁBarrelListǁ_balance_list__mutmut_13': xǁBarrelListǁ_balance_list__mutmut_13, 
        'xǁBarrelListǁ_balance_list__mutmut_14': xǁBarrelListǁ_balance_list__mutmut_14, 
        'xǁBarrelListǁ_balance_list__mutmut_15': xǁBarrelListǁ_balance_list__mutmut_15, 
        'xǁBarrelListǁ_balance_list__mutmut_16': xǁBarrelListǁ_balance_list__mutmut_16, 
        'xǁBarrelListǁ_balance_list__mutmut_17': xǁBarrelListǁ_balance_list__mutmut_17, 
        'xǁBarrelListǁ_balance_list__mutmut_18': xǁBarrelListǁ_balance_list__mutmut_18, 
        'xǁBarrelListǁ_balance_list__mutmut_19': xǁBarrelListǁ_balance_list__mutmut_19, 
        'xǁBarrelListǁ_balance_list__mutmut_20': xǁBarrelListǁ_balance_list__mutmut_20, 
        'xǁBarrelListǁ_balance_list__mutmut_21': xǁBarrelListǁ_balance_list__mutmut_21, 
        'xǁBarrelListǁ_balance_list__mutmut_22': xǁBarrelListǁ_balance_list__mutmut_22
    }
    
    def _balance_list(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ_balance_list__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ_balance_list__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _balance_list.__signature__ = _mutmut_signature(xǁBarrelListǁ_balance_list__mutmut_orig)
    xǁBarrelListǁ_balance_list__mutmut_orig.__name__ = 'xǁBarrelListǁ_balance_list'

    def xǁBarrelListǁinsert__mutmut_orig(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_1(self, index, item):
        if len(self.lists) != 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_2(self, index, item):
        if len(self.lists) == 2:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_3(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(None, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_4(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, None)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_5(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_6(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, )
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_7(self, index, item):
        if len(self.lists) == 1:
            self.lists[1].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_8(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(None)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_9(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(1)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_10(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = None
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_11(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(None)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_12(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is not None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_13(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(None, item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_14(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, None)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_15(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(item)
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_16(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, )
            self._balance_list(list_idx)
        return

    def xǁBarrelListǁinsert__mutmut_17(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(None)
        return
    
    xǁBarrelListǁinsert__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁinsert__mutmut_1': xǁBarrelListǁinsert__mutmut_1, 
        'xǁBarrelListǁinsert__mutmut_2': xǁBarrelListǁinsert__mutmut_2, 
        'xǁBarrelListǁinsert__mutmut_3': xǁBarrelListǁinsert__mutmut_3, 
        'xǁBarrelListǁinsert__mutmut_4': xǁBarrelListǁinsert__mutmut_4, 
        'xǁBarrelListǁinsert__mutmut_5': xǁBarrelListǁinsert__mutmut_5, 
        'xǁBarrelListǁinsert__mutmut_6': xǁBarrelListǁinsert__mutmut_6, 
        'xǁBarrelListǁinsert__mutmut_7': xǁBarrelListǁinsert__mutmut_7, 
        'xǁBarrelListǁinsert__mutmut_8': xǁBarrelListǁinsert__mutmut_8, 
        'xǁBarrelListǁinsert__mutmut_9': xǁBarrelListǁinsert__mutmut_9, 
        'xǁBarrelListǁinsert__mutmut_10': xǁBarrelListǁinsert__mutmut_10, 
        'xǁBarrelListǁinsert__mutmut_11': xǁBarrelListǁinsert__mutmut_11, 
        'xǁBarrelListǁinsert__mutmut_12': xǁBarrelListǁinsert__mutmut_12, 
        'xǁBarrelListǁinsert__mutmut_13': xǁBarrelListǁinsert__mutmut_13, 
        'xǁBarrelListǁinsert__mutmut_14': xǁBarrelListǁinsert__mutmut_14, 
        'xǁBarrelListǁinsert__mutmut_15': xǁBarrelListǁinsert__mutmut_15, 
        'xǁBarrelListǁinsert__mutmut_16': xǁBarrelListǁinsert__mutmut_16, 
        'xǁBarrelListǁinsert__mutmut_17': xǁBarrelListǁinsert__mutmut_17
    }
    
    def insert(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁinsert__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁinsert__mutmut_mutants"), args, kwargs, self)
        return result 
    
    insert.__signature__ = _mutmut_signature(xǁBarrelListǁinsert__mutmut_orig)
    xǁBarrelListǁinsert__mutmut_orig.__name__ = 'xǁBarrelListǁinsert'

    def xǁBarrelListǁappend__mutmut_orig(self, item):
        self.lists[-1].append(item)

    def xǁBarrelListǁappend__mutmut_1(self, item):
        self.lists[-1].append(None)

    def xǁBarrelListǁappend__mutmut_2(self, item):
        self.lists[+1].append(item)

    def xǁBarrelListǁappend__mutmut_3(self, item):
        self.lists[-2].append(item)
    
    xǁBarrelListǁappend__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁappend__mutmut_1': xǁBarrelListǁappend__mutmut_1, 
        'xǁBarrelListǁappend__mutmut_2': xǁBarrelListǁappend__mutmut_2, 
        'xǁBarrelListǁappend__mutmut_3': xǁBarrelListǁappend__mutmut_3
    }
    
    def append(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁappend__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁappend__mutmut_mutants"), args, kwargs, self)
        return result 
    
    append.__signature__ = _mutmut_signature(xǁBarrelListǁappend__mutmut_orig)
    xǁBarrelListǁappend__mutmut_orig.__name__ = 'xǁBarrelListǁappend'

    def xǁBarrelListǁextend__mutmut_orig(self, iterable):
        self.lists[-1].extend(iterable)

    def xǁBarrelListǁextend__mutmut_1(self, iterable):
        self.lists[-1].extend(None)

    def xǁBarrelListǁextend__mutmut_2(self, iterable):
        self.lists[+1].extend(iterable)

    def xǁBarrelListǁextend__mutmut_3(self, iterable):
        self.lists[-2].extend(iterable)
    
    xǁBarrelListǁextend__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁextend__mutmut_1': xǁBarrelListǁextend__mutmut_1, 
        'xǁBarrelListǁextend__mutmut_2': xǁBarrelListǁextend__mutmut_2, 
        'xǁBarrelListǁextend__mutmut_3': xǁBarrelListǁextend__mutmut_3
    }
    
    def extend(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁextend__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁextend__mutmut_mutants"), args, kwargs, self)
        return result 
    
    extend.__signature__ = _mutmut_signature(xǁBarrelListǁextend__mutmut_orig)
    xǁBarrelListǁextend__mutmut_orig.__name__ = 'xǁBarrelListǁextend'

    def xǁBarrelListǁpop__mutmut_orig(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_1(self, *a):
        lists = None
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_2(self, *a):
        lists = self.lists
        if len(lists) == 1 or not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_3(self, *a):
        lists = self.lists
        if len(lists) != 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_4(self, *a):
        lists = self.lists
        if len(lists) == 2 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_5(self, *a):
        lists = self.lists
        if len(lists) == 1 and a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_6(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[1].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_7(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = None
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_8(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a or a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_9(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[1]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_10(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None and index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_11(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () and index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_12(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index != () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_13(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is not None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_14(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index != -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_15(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == +1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_16(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -2:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_17(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = None
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_18(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[+1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_19(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-2].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_20(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 or not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_21(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) >= 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_22(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 2 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_23(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_24(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[+1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_25(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-2]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_26(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = None
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_27(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(None)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_28(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is not None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_29(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = None
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_30(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(None)
            self._balance_list(list_idx)
        return ret

    def xǁBarrelListǁpop__mutmut_31(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(None)
        return ret
    
    xǁBarrelListǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁpop__mutmut_1': xǁBarrelListǁpop__mutmut_1, 
        'xǁBarrelListǁpop__mutmut_2': xǁBarrelListǁpop__mutmut_2, 
        'xǁBarrelListǁpop__mutmut_3': xǁBarrelListǁpop__mutmut_3, 
        'xǁBarrelListǁpop__mutmut_4': xǁBarrelListǁpop__mutmut_4, 
        'xǁBarrelListǁpop__mutmut_5': xǁBarrelListǁpop__mutmut_5, 
        'xǁBarrelListǁpop__mutmut_6': xǁBarrelListǁpop__mutmut_6, 
        'xǁBarrelListǁpop__mutmut_7': xǁBarrelListǁpop__mutmut_7, 
        'xǁBarrelListǁpop__mutmut_8': xǁBarrelListǁpop__mutmut_8, 
        'xǁBarrelListǁpop__mutmut_9': xǁBarrelListǁpop__mutmut_9, 
        'xǁBarrelListǁpop__mutmut_10': xǁBarrelListǁpop__mutmut_10, 
        'xǁBarrelListǁpop__mutmut_11': xǁBarrelListǁpop__mutmut_11, 
        'xǁBarrelListǁpop__mutmut_12': xǁBarrelListǁpop__mutmut_12, 
        'xǁBarrelListǁpop__mutmut_13': xǁBarrelListǁpop__mutmut_13, 
        'xǁBarrelListǁpop__mutmut_14': xǁBarrelListǁpop__mutmut_14, 
        'xǁBarrelListǁpop__mutmut_15': xǁBarrelListǁpop__mutmut_15, 
        'xǁBarrelListǁpop__mutmut_16': xǁBarrelListǁpop__mutmut_16, 
        'xǁBarrelListǁpop__mutmut_17': xǁBarrelListǁpop__mutmut_17, 
        'xǁBarrelListǁpop__mutmut_18': xǁBarrelListǁpop__mutmut_18, 
        'xǁBarrelListǁpop__mutmut_19': xǁBarrelListǁpop__mutmut_19, 
        'xǁBarrelListǁpop__mutmut_20': xǁBarrelListǁpop__mutmut_20, 
        'xǁBarrelListǁpop__mutmut_21': xǁBarrelListǁpop__mutmut_21, 
        'xǁBarrelListǁpop__mutmut_22': xǁBarrelListǁpop__mutmut_22, 
        'xǁBarrelListǁpop__mutmut_23': xǁBarrelListǁpop__mutmut_23, 
        'xǁBarrelListǁpop__mutmut_24': xǁBarrelListǁpop__mutmut_24, 
        'xǁBarrelListǁpop__mutmut_25': xǁBarrelListǁpop__mutmut_25, 
        'xǁBarrelListǁpop__mutmut_26': xǁBarrelListǁpop__mutmut_26, 
        'xǁBarrelListǁpop__mutmut_27': xǁBarrelListǁpop__mutmut_27, 
        'xǁBarrelListǁpop__mutmut_28': xǁBarrelListǁpop__mutmut_28, 
        'xǁBarrelListǁpop__mutmut_29': xǁBarrelListǁpop__mutmut_29, 
        'xǁBarrelListǁpop__mutmut_30': xǁBarrelListǁpop__mutmut_30, 
        'xǁBarrelListǁpop__mutmut_31': xǁBarrelListǁpop__mutmut_31
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁpop__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁBarrelListǁpop__mutmut_orig)
    xǁBarrelListǁpop__mutmut_orig.__name__ = 'xǁBarrelListǁpop'

    def xǁBarrelListǁiter_slice__mutmut_orig(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_1(self, start, stop, step=None):
        iterable = None  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_2(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is not None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_3(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = None
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_4(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 1
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_5(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is not None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_6(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = None
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_7(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None or step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_8(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_9(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step <= 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_10(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 1:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_11(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = None
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_12(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = +step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_13(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = None
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_14(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = +start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_15(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop + 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_16(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, +stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_17(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 2
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_18(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = None
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_19(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(None)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_20(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start <= 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_21(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 1:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_22(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start = len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_23(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start -= len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_24(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop <= 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_25(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 1:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_26(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop = len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_27(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop -= len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_28(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(None, start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_29(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, None, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_30(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, None, step)

    def xǁBarrelListǁiter_slice__mutmut_31(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, None)

    def xǁBarrelListǁiter_slice__mutmut_32(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(start, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_33(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, stop, step)

    def xǁBarrelListǁiter_slice__mutmut_34(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, step)

    def xǁBarrelListǁiter_slice__mutmut_35(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, )
    
    xǁBarrelListǁiter_slice__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁiter_slice__mutmut_1': xǁBarrelListǁiter_slice__mutmut_1, 
        'xǁBarrelListǁiter_slice__mutmut_2': xǁBarrelListǁiter_slice__mutmut_2, 
        'xǁBarrelListǁiter_slice__mutmut_3': xǁBarrelListǁiter_slice__mutmut_3, 
        'xǁBarrelListǁiter_slice__mutmut_4': xǁBarrelListǁiter_slice__mutmut_4, 
        'xǁBarrelListǁiter_slice__mutmut_5': xǁBarrelListǁiter_slice__mutmut_5, 
        'xǁBarrelListǁiter_slice__mutmut_6': xǁBarrelListǁiter_slice__mutmut_6, 
        'xǁBarrelListǁiter_slice__mutmut_7': xǁBarrelListǁiter_slice__mutmut_7, 
        'xǁBarrelListǁiter_slice__mutmut_8': xǁBarrelListǁiter_slice__mutmut_8, 
        'xǁBarrelListǁiter_slice__mutmut_9': xǁBarrelListǁiter_slice__mutmut_9, 
        'xǁBarrelListǁiter_slice__mutmut_10': xǁBarrelListǁiter_slice__mutmut_10, 
        'xǁBarrelListǁiter_slice__mutmut_11': xǁBarrelListǁiter_slice__mutmut_11, 
        'xǁBarrelListǁiter_slice__mutmut_12': xǁBarrelListǁiter_slice__mutmut_12, 
        'xǁBarrelListǁiter_slice__mutmut_13': xǁBarrelListǁiter_slice__mutmut_13, 
        'xǁBarrelListǁiter_slice__mutmut_14': xǁBarrelListǁiter_slice__mutmut_14, 
        'xǁBarrelListǁiter_slice__mutmut_15': xǁBarrelListǁiter_slice__mutmut_15, 
        'xǁBarrelListǁiter_slice__mutmut_16': xǁBarrelListǁiter_slice__mutmut_16, 
        'xǁBarrelListǁiter_slice__mutmut_17': xǁBarrelListǁiter_slice__mutmut_17, 
        'xǁBarrelListǁiter_slice__mutmut_18': xǁBarrelListǁiter_slice__mutmut_18, 
        'xǁBarrelListǁiter_slice__mutmut_19': xǁBarrelListǁiter_slice__mutmut_19, 
        'xǁBarrelListǁiter_slice__mutmut_20': xǁBarrelListǁiter_slice__mutmut_20, 
        'xǁBarrelListǁiter_slice__mutmut_21': xǁBarrelListǁiter_slice__mutmut_21, 
        'xǁBarrelListǁiter_slice__mutmut_22': xǁBarrelListǁiter_slice__mutmut_22, 
        'xǁBarrelListǁiter_slice__mutmut_23': xǁBarrelListǁiter_slice__mutmut_23, 
        'xǁBarrelListǁiter_slice__mutmut_24': xǁBarrelListǁiter_slice__mutmut_24, 
        'xǁBarrelListǁiter_slice__mutmut_25': xǁBarrelListǁiter_slice__mutmut_25, 
        'xǁBarrelListǁiter_slice__mutmut_26': xǁBarrelListǁiter_slice__mutmut_26, 
        'xǁBarrelListǁiter_slice__mutmut_27': xǁBarrelListǁiter_slice__mutmut_27, 
        'xǁBarrelListǁiter_slice__mutmut_28': xǁBarrelListǁiter_slice__mutmut_28, 
        'xǁBarrelListǁiter_slice__mutmut_29': xǁBarrelListǁiter_slice__mutmut_29, 
        'xǁBarrelListǁiter_slice__mutmut_30': xǁBarrelListǁiter_slice__mutmut_30, 
        'xǁBarrelListǁiter_slice__mutmut_31': xǁBarrelListǁiter_slice__mutmut_31, 
        'xǁBarrelListǁiter_slice__mutmut_32': xǁBarrelListǁiter_slice__mutmut_32, 
        'xǁBarrelListǁiter_slice__mutmut_33': xǁBarrelListǁiter_slice__mutmut_33, 
        'xǁBarrelListǁiter_slice__mutmut_34': xǁBarrelListǁiter_slice__mutmut_34, 
        'xǁBarrelListǁiter_slice__mutmut_35': xǁBarrelListǁiter_slice__mutmut_35
    }
    
    def iter_slice(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁiter_slice__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁiter_slice__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iter_slice.__signature__ = _mutmut_signature(xǁBarrelListǁiter_slice__mutmut_orig)
    xǁBarrelListǁiter_slice__mutmut_orig.__name__ = 'xǁBarrelListǁiter_slice'

    def xǁBarrelListǁdel_slice__mutmut_orig(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_1(self, start, stop, step=None):
        if step is not None or abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_2(self, start, stop, step=None):
        if step is None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_3(self, start, stop, step=None):
        if step is not None and abs(None) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_4(self, start, stop, step=None):
        if step is not None and abs(step) >= 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_5(self, start, stop, step=None):
        if step is not None and abs(step) > 2:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_6(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = None
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_7(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(None,
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_8(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             None)
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_9(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_10(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             )
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_11(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(None, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_12(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, None, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_13(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, None),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_14(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_15(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_16(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, ),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_17(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(1, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_18(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(None, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_19(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, None))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_20(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_21(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_22(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, ))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_23(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = None
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_24(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[1][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_25(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(None)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_26(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(1)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_27(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is not None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_28(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = None
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_29(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 1
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_30(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is not None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_31(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = None
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_32(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = None
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_33(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(None)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_34(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = None
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_35(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(None)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_36(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is not None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_37(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is not None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_38(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx != stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_39(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx <= stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_40(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx - 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_41(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 2:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_42(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert True, ('start list index should never translate to'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_43(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('XXstart list index should never translate toXX'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_44(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('START LIST INDEX SHOULD NEVER TRANSLATE TO'
                           ' greater than stop list index')

    def xǁBarrelListǁdel_slice__mutmut_45(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           'XX greater than stop list indexXX')

    def xǁBarrelListǁdel_slice__mutmut_46(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' GREATER THAN STOP LIST INDEX')
    
    xǁBarrelListǁdel_slice__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁdel_slice__mutmut_1': xǁBarrelListǁdel_slice__mutmut_1, 
        'xǁBarrelListǁdel_slice__mutmut_2': xǁBarrelListǁdel_slice__mutmut_2, 
        'xǁBarrelListǁdel_slice__mutmut_3': xǁBarrelListǁdel_slice__mutmut_3, 
        'xǁBarrelListǁdel_slice__mutmut_4': xǁBarrelListǁdel_slice__mutmut_4, 
        'xǁBarrelListǁdel_slice__mutmut_5': xǁBarrelListǁdel_slice__mutmut_5, 
        'xǁBarrelListǁdel_slice__mutmut_6': xǁBarrelListǁdel_slice__mutmut_6, 
        'xǁBarrelListǁdel_slice__mutmut_7': xǁBarrelListǁdel_slice__mutmut_7, 
        'xǁBarrelListǁdel_slice__mutmut_8': xǁBarrelListǁdel_slice__mutmut_8, 
        'xǁBarrelListǁdel_slice__mutmut_9': xǁBarrelListǁdel_slice__mutmut_9, 
        'xǁBarrelListǁdel_slice__mutmut_10': xǁBarrelListǁdel_slice__mutmut_10, 
        'xǁBarrelListǁdel_slice__mutmut_11': xǁBarrelListǁdel_slice__mutmut_11, 
        'xǁBarrelListǁdel_slice__mutmut_12': xǁBarrelListǁdel_slice__mutmut_12, 
        'xǁBarrelListǁdel_slice__mutmut_13': xǁBarrelListǁdel_slice__mutmut_13, 
        'xǁBarrelListǁdel_slice__mutmut_14': xǁBarrelListǁdel_slice__mutmut_14, 
        'xǁBarrelListǁdel_slice__mutmut_15': xǁBarrelListǁdel_slice__mutmut_15, 
        'xǁBarrelListǁdel_slice__mutmut_16': xǁBarrelListǁdel_slice__mutmut_16, 
        'xǁBarrelListǁdel_slice__mutmut_17': xǁBarrelListǁdel_slice__mutmut_17, 
        'xǁBarrelListǁdel_slice__mutmut_18': xǁBarrelListǁdel_slice__mutmut_18, 
        'xǁBarrelListǁdel_slice__mutmut_19': xǁBarrelListǁdel_slice__mutmut_19, 
        'xǁBarrelListǁdel_slice__mutmut_20': xǁBarrelListǁdel_slice__mutmut_20, 
        'xǁBarrelListǁdel_slice__mutmut_21': xǁBarrelListǁdel_slice__mutmut_21, 
        'xǁBarrelListǁdel_slice__mutmut_22': xǁBarrelListǁdel_slice__mutmut_22, 
        'xǁBarrelListǁdel_slice__mutmut_23': xǁBarrelListǁdel_slice__mutmut_23, 
        'xǁBarrelListǁdel_slice__mutmut_24': xǁBarrelListǁdel_slice__mutmut_24, 
        'xǁBarrelListǁdel_slice__mutmut_25': xǁBarrelListǁdel_slice__mutmut_25, 
        'xǁBarrelListǁdel_slice__mutmut_26': xǁBarrelListǁdel_slice__mutmut_26, 
        'xǁBarrelListǁdel_slice__mutmut_27': xǁBarrelListǁdel_slice__mutmut_27, 
        'xǁBarrelListǁdel_slice__mutmut_28': xǁBarrelListǁdel_slice__mutmut_28, 
        'xǁBarrelListǁdel_slice__mutmut_29': xǁBarrelListǁdel_slice__mutmut_29, 
        'xǁBarrelListǁdel_slice__mutmut_30': xǁBarrelListǁdel_slice__mutmut_30, 
        'xǁBarrelListǁdel_slice__mutmut_31': xǁBarrelListǁdel_slice__mutmut_31, 
        'xǁBarrelListǁdel_slice__mutmut_32': xǁBarrelListǁdel_slice__mutmut_32, 
        'xǁBarrelListǁdel_slice__mutmut_33': xǁBarrelListǁdel_slice__mutmut_33, 
        'xǁBarrelListǁdel_slice__mutmut_34': xǁBarrelListǁdel_slice__mutmut_34, 
        'xǁBarrelListǁdel_slice__mutmut_35': xǁBarrelListǁdel_slice__mutmut_35, 
        'xǁBarrelListǁdel_slice__mutmut_36': xǁBarrelListǁdel_slice__mutmut_36, 
        'xǁBarrelListǁdel_slice__mutmut_37': xǁBarrelListǁdel_slice__mutmut_37, 
        'xǁBarrelListǁdel_slice__mutmut_38': xǁBarrelListǁdel_slice__mutmut_38, 
        'xǁBarrelListǁdel_slice__mutmut_39': xǁBarrelListǁdel_slice__mutmut_39, 
        'xǁBarrelListǁdel_slice__mutmut_40': xǁBarrelListǁdel_slice__mutmut_40, 
        'xǁBarrelListǁdel_slice__mutmut_41': xǁBarrelListǁdel_slice__mutmut_41, 
        'xǁBarrelListǁdel_slice__mutmut_42': xǁBarrelListǁdel_slice__mutmut_42, 
        'xǁBarrelListǁdel_slice__mutmut_43': xǁBarrelListǁdel_slice__mutmut_43, 
        'xǁBarrelListǁdel_slice__mutmut_44': xǁBarrelListǁdel_slice__mutmut_44, 
        'xǁBarrelListǁdel_slice__mutmut_45': xǁBarrelListǁdel_slice__mutmut_45, 
        'xǁBarrelListǁdel_slice__mutmut_46': xǁBarrelListǁdel_slice__mutmut_46
    }
    
    def del_slice(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁdel_slice__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁdel_slice__mutmut_mutants"), args, kwargs, self)
        return result 
    
    del_slice.__signature__ = _mutmut_signature(xǁBarrelListǁdel_slice__mutmut_orig)
    xǁBarrelListǁdel_slice__mutmut_orig.__name__ = 'xǁBarrelListǁdel_slice'

    __delslice__ = del_slice

    @classmethod
    def from_iterable(cls, it):
        return cls(it)

    def xǁBarrelListǁ__iter____mutmut_orig(self):
        return chain.from_iterable(self.lists)

    def xǁBarrelListǁ__iter____mutmut_1(self):
        return chain.from_iterable(None)
    
    xǁBarrelListǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__iter____mutmut_1': xǁBarrelListǁ__iter____mutmut_1
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁBarrelListǁ__iter____mutmut_orig)
    xǁBarrelListǁ__iter____mutmut_orig.__name__ = 'xǁBarrelListǁ__iter__'

    def xǁBarrelListǁ__reversed____mutmut_orig(self):
        return chain.from_iterable(reversed(l) for l in reversed(self.lists))

    def xǁBarrelListǁ__reversed____mutmut_1(self):
        return chain.from_iterable(None)

    def xǁBarrelListǁ__reversed____mutmut_2(self):
        return chain.from_iterable(reversed(None) for l in reversed(self.lists))

    def xǁBarrelListǁ__reversed____mutmut_3(self):
        return chain.from_iterable(reversed(l) for l in reversed(None))
    
    xǁBarrelListǁ__reversed____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__reversed____mutmut_1': xǁBarrelListǁ__reversed____mutmut_1, 
        'xǁBarrelListǁ__reversed____mutmut_2': xǁBarrelListǁ__reversed____mutmut_2, 
        'xǁBarrelListǁ__reversed____mutmut_3': xǁBarrelListǁ__reversed____mutmut_3
    }
    
    def __reversed__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__reversed____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__reversed____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __reversed__.__signature__ = _mutmut_signature(xǁBarrelListǁ__reversed____mutmut_orig)
    xǁBarrelListǁ__reversed____mutmut_orig.__name__ = 'xǁBarrelListǁ__reversed__'

    def xǁBarrelListǁ__len____mutmut_orig(self):
        return sum([len(l) for l in self.lists])

    def xǁBarrelListǁ__len____mutmut_1(self):
        return sum(None)
    
    xǁBarrelListǁ__len____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__len____mutmut_1': xǁBarrelListǁ__len____mutmut_1
    }
    
    def __len__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__len____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__len____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __len__.__signature__ = _mutmut_signature(xǁBarrelListǁ__len____mutmut_orig)
    xǁBarrelListǁ__len____mutmut_orig.__name__ = 'xǁBarrelListǁ__len__'

    def xǁBarrelListǁ__contains____mutmut_orig(self, item):
        for cur in self.lists:
            if item in cur:
                return True
        return False

    def xǁBarrelListǁ__contains____mutmut_1(self, item):
        for cur in self.lists:
            if item not in cur:
                return True
        return False

    def xǁBarrelListǁ__contains____mutmut_2(self, item):
        for cur in self.lists:
            if item in cur:
                return False
        return False

    def xǁBarrelListǁ__contains____mutmut_3(self, item):
        for cur in self.lists:
            if item in cur:
                return True
        return True
    
    xǁBarrelListǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__contains____mutmut_1': xǁBarrelListǁ__contains____mutmut_1, 
        'xǁBarrelListǁ__contains____mutmut_2': xǁBarrelListǁ__contains____mutmut_2, 
        'xǁBarrelListǁ__contains____mutmut_3': xǁBarrelListǁ__contains____mutmut_3
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁBarrelListǁ__contains____mutmut_orig)
    xǁBarrelListǁ__contains____mutmut_orig.__name__ = 'xǁBarrelListǁ__contains__'

    def xǁBarrelListǁ__getitem____mutmut_orig(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_1(self, index):
        try:
            start, stop, step = None
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_2(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = None
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_3(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(None)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_4(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.rindex(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_5(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = None
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_6(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(None, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_7(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, None, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_8(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, None)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_9(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_10(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_11(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, )
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_12(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = None
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_13(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(None)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_14(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = None
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_15(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(None)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__getitem____mutmut_16(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is not None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]
    
    xǁBarrelListǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__getitem____mutmut_1': xǁBarrelListǁ__getitem____mutmut_1, 
        'xǁBarrelListǁ__getitem____mutmut_2': xǁBarrelListǁ__getitem____mutmut_2, 
        'xǁBarrelListǁ__getitem____mutmut_3': xǁBarrelListǁ__getitem____mutmut_3, 
        'xǁBarrelListǁ__getitem____mutmut_4': xǁBarrelListǁ__getitem____mutmut_4, 
        'xǁBarrelListǁ__getitem____mutmut_5': xǁBarrelListǁ__getitem____mutmut_5, 
        'xǁBarrelListǁ__getitem____mutmut_6': xǁBarrelListǁ__getitem____mutmut_6, 
        'xǁBarrelListǁ__getitem____mutmut_7': xǁBarrelListǁ__getitem____mutmut_7, 
        'xǁBarrelListǁ__getitem____mutmut_8': xǁBarrelListǁ__getitem____mutmut_8, 
        'xǁBarrelListǁ__getitem____mutmut_9': xǁBarrelListǁ__getitem____mutmut_9, 
        'xǁBarrelListǁ__getitem____mutmut_10': xǁBarrelListǁ__getitem____mutmut_10, 
        'xǁBarrelListǁ__getitem____mutmut_11': xǁBarrelListǁ__getitem____mutmut_11, 
        'xǁBarrelListǁ__getitem____mutmut_12': xǁBarrelListǁ__getitem____mutmut_12, 
        'xǁBarrelListǁ__getitem____mutmut_13': xǁBarrelListǁ__getitem____mutmut_13, 
        'xǁBarrelListǁ__getitem____mutmut_14': xǁBarrelListǁ__getitem____mutmut_14, 
        'xǁBarrelListǁ__getitem____mutmut_15': xǁBarrelListǁ__getitem____mutmut_15, 
        'xǁBarrelListǁ__getitem____mutmut_16': xǁBarrelListǁ__getitem____mutmut_16
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁBarrelListǁ__getitem____mutmut_orig)
    xǁBarrelListǁ__getitem____mutmut_orig.__name__ = 'xǁBarrelListǁ__getitem__'

    def xǁBarrelListǁ__delitem____mutmut_orig(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_1(self, index):
        try:
            start, stop, step = None
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_2(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = None
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_3(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(None)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_4(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.rindex(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_5(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(None, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_6(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, None, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_7(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, None)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_8(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_9(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_10(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, )
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_11(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = None
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_12(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(None)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def xǁBarrelListǁ__delitem____mutmut_13(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is not None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]
    
    xǁBarrelListǁ__delitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__delitem____mutmut_1': xǁBarrelListǁ__delitem____mutmut_1, 
        'xǁBarrelListǁ__delitem____mutmut_2': xǁBarrelListǁ__delitem____mutmut_2, 
        'xǁBarrelListǁ__delitem____mutmut_3': xǁBarrelListǁ__delitem____mutmut_3, 
        'xǁBarrelListǁ__delitem____mutmut_4': xǁBarrelListǁ__delitem____mutmut_4, 
        'xǁBarrelListǁ__delitem____mutmut_5': xǁBarrelListǁ__delitem____mutmut_5, 
        'xǁBarrelListǁ__delitem____mutmut_6': xǁBarrelListǁ__delitem____mutmut_6, 
        'xǁBarrelListǁ__delitem____mutmut_7': xǁBarrelListǁ__delitem____mutmut_7, 
        'xǁBarrelListǁ__delitem____mutmut_8': xǁBarrelListǁ__delitem____mutmut_8, 
        'xǁBarrelListǁ__delitem____mutmut_9': xǁBarrelListǁ__delitem____mutmut_9, 
        'xǁBarrelListǁ__delitem____mutmut_10': xǁBarrelListǁ__delitem____mutmut_10, 
        'xǁBarrelListǁ__delitem____mutmut_11': xǁBarrelListǁ__delitem____mutmut_11, 
        'xǁBarrelListǁ__delitem____mutmut_12': xǁBarrelListǁ__delitem____mutmut_12, 
        'xǁBarrelListǁ__delitem____mutmut_13': xǁBarrelListǁ__delitem____mutmut_13
    }
    
    def __delitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__delitem____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__delitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delitem__.__signature__ = _mutmut_signature(xǁBarrelListǁ__delitem____mutmut_orig)
    xǁBarrelListǁ__delitem____mutmut_orig.__name__ = 'xǁBarrelListǁ__delitem__'

    def xǁBarrelListǁ__setitem____mutmut_orig(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_1(self, index, item):
        try:
            start, stop, step = None
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_2(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = None
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_3(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(None)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_4(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.rindex(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_5(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) != 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_6(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 2:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_7(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = None
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_8(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[1][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_9(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = None
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_10(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(None)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_11(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = None
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_12(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = None
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_13(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(None)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_14(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(1)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_15(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = None
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_16(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(None)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_17(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is not None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def xǁBarrelListǁ__setitem____mutmut_18(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = None
    
    xǁBarrelListǁ__setitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__setitem____mutmut_1': xǁBarrelListǁ__setitem____mutmut_1, 
        'xǁBarrelListǁ__setitem____mutmut_2': xǁBarrelListǁ__setitem____mutmut_2, 
        'xǁBarrelListǁ__setitem____mutmut_3': xǁBarrelListǁ__setitem____mutmut_3, 
        'xǁBarrelListǁ__setitem____mutmut_4': xǁBarrelListǁ__setitem____mutmut_4, 
        'xǁBarrelListǁ__setitem____mutmut_5': xǁBarrelListǁ__setitem____mutmut_5, 
        'xǁBarrelListǁ__setitem____mutmut_6': xǁBarrelListǁ__setitem____mutmut_6, 
        'xǁBarrelListǁ__setitem____mutmut_7': xǁBarrelListǁ__setitem____mutmut_7, 
        'xǁBarrelListǁ__setitem____mutmut_8': xǁBarrelListǁ__setitem____mutmut_8, 
        'xǁBarrelListǁ__setitem____mutmut_9': xǁBarrelListǁ__setitem____mutmut_9, 
        'xǁBarrelListǁ__setitem____mutmut_10': xǁBarrelListǁ__setitem____mutmut_10, 
        'xǁBarrelListǁ__setitem____mutmut_11': xǁBarrelListǁ__setitem____mutmut_11, 
        'xǁBarrelListǁ__setitem____mutmut_12': xǁBarrelListǁ__setitem____mutmut_12, 
        'xǁBarrelListǁ__setitem____mutmut_13': xǁBarrelListǁ__setitem____mutmut_13, 
        'xǁBarrelListǁ__setitem____mutmut_14': xǁBarrelListǁ__setitem____mutmut_14, 
        'xǁBarrelListǁ__setitem____mutmut_15': xǁBarrelListǁ__setitem____mutmut_15, 
        'xǁBarrelListǁ__setitem____mutmut_16': xǁBarrelListǁ__setitem____mutmut_16, 
        'xǁBarrelListǁ__setitem____mutmut_17': xǁBarrelListǁ__setitem____mutmut_17, 
        'xǁBarrelListǁ__setitem____mutmut_18': xǁBarrelListǁ__setitem____mutmut_18
    }
    
    def __setitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__setitem____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__setitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setitem__.__signature__ = _mutmut_signature(xǁBarrelListǁ__setitem____mutmut_orig)
    xǁBarrelListǁ__setitem____mutmut_orig.__name__ = 'xǁBarrelListǁ__setitem__'

    def xǁBarrelListǁ__getslice____mutmut_orig(self, start, stop):
        iter_slice = self.iter_slice(start, stop, 1)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_1(self, start, stop):
        iter_slice = None
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_2(self, start, stop):
        iter_slice = self.iter_slice(None, stop, 1)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_3(self, start, stop):
        iter_slice = self.iter_slice(start, None, 1)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_4(self, start, stop):
        iter_slice = self.iter_slice(start, stop, None)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_5(self, start, stop):
        iter_slice = self.iter_slice(stop, 1)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_6(self, start, stop):
        iter_slice = self.iter_slice(start, 1)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_7(self, start, stop):
        iter_slice = self.iter_slice(start, stop, )
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_8(self, start, stop):
        iter_slice = self.iter_slice(start, stop, 2)
        return self.from_iterable(iter_slice)

    def xǁBarrelListǁ__getslice____mutmut_9(self, start, stop):
        iter_slice = self.iter_slice(start, stop, 1)
        return self.from_iterable(None)
    
    xǁBarrelListǁ__getslice____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__getslice____mutmut_1': xǁBarrelListǁ__getslice____mutmut_1, 
        'xǁBarrelListǁ__getslice____mutmut_2': xǁBarrelListǁ__getslice____mutmut_2, 
        'xǁBarrelListǁ__getslice____mutmut_3': xǁBarrelListǁ__getslice____mutmut_3, 
        'xǁBarrelListǁ__getslice____mutmut_4': xǁBarrelListǁ__getslice____mutmut_4, 
        'xǁBarrelListǁ__getslice____mutmut_5': xǁBarrelListǁ__getslice____mutmut_5, 
        'xǁBarrelListǁ__getslice____mutmut_6': xǁBarrelListǁ__getslice____mutmut_6, 
        'xǁBarrelListǁ__getslice____mutmut_7': xǁBarrelListǁ__getslice____mutmut_7, 
        'xǁBarrelListǁ__getslice____mutmut_8': xǁBarrelListǁ__getslice____mutmut_8, 
        'xǁBarrelListǁ__getslice____mutmut_9': xǁBarrelListǁ__getslice____mutmut_9
    }
    
    def __getslice__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__getslice____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__getslice____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getslice__.__signature__ = _mutmut_signature(xǁBarrelListǁ__getslice____mutmut_orig)
    xǁBarrelListǁ__getslice____mutmut_orig.__name__ = 'xǁBarrelListǁ__getslice__'

    def xǁBarrelListǁ__setslice____mutmut_orig(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_1(self, start, stop, sequence):
        if len(self.lists) != 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_2(self, start, stop, sequence):
        if len(self.lists) == 2:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_3(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = None
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_4(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[1][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_5(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = None
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_6(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(None)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_7(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = None
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_8(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = None
        self._balance_list(0)
        return

    def xǁBarrelListǁ__setslice____mutmut_9(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(None)
        return

    def xǁBarrelListǁ__setslice____mutmut_10(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(1)
        return
    
    xǁBarrelListǁ__setslice____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__setslice____mutmut_1': xǁBarrelListǁ__setslice____mutmut_1, 
        'xǁBarrelListǁ__setslice____mutmut_2': xǁBarrelListǁ__setslice____mutmut_2, 
        'xǁBarrelListǁ__setslice____mutmut_3': xǁBarrelListǁ__setslice____mutmut_3, 
        'xǁBarrelListǁ__setslice____mutmut_4': xǁBarrelListǁ__setslice____mutmut_4, 
        'xǁBarrelListǁ__setslice____mutmut_5': xǁBarrelListǁ__setslice____mutmut_5, 
        'xǁBarrelListǁ__setslice____mutmut_6': xǁBarrelListǁ__setslice____mutmut_6, 
        'xǁBarrelListǁ__setslice____mutmut_7': xǁBarrelListǁ__setslice____mutmut_7, 
        'xǁBarrelListǁ__setslice____mutmut_8': xǁBarrelListǁ__setslice____mutmut_8, 
        'xǁBarrelListǁ__setslice____mutmut_9': xǁBarrelListǁ__setslice____mutmut_9, 
        'xǁBarrelListǁ__setslice____mutmut_10': xǁBarrelListǁ__setslice____mutmut_10
    }
    
    def __setslice__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__setslice____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__setslice____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setslice__.__signature__ = _mutmut_signature(xǁBarrelListǁ__setslice____mutmut_orig)
    xǁBarrelListǁ__setslice____mutmut_orig.__name__ = 'xǁBarrelListǁ__setslice__'

    def xǁBarrelListǁ__repr____mutmut_orig(self):
        return f'{self.__class__.__name__}({list(self)!r})'

    def xǁBarrelListǁ__repr____mutmut_1(self):
        return f'{self.__class__.__name__}({list(None)!r})'
    
    xǁBarrelListǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁ__repr____mutmut_1': xǁBarrelListǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁBarrelListǁ__repr____mutmut_orig)
    xǁBarrelListǁ__repr____mutmut_orig.__name__ = 'xǁBarrelListǁ__repr__'

    def xǁBarrelListǁsort__mutmut_orig(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_1(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) != 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_2(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 2:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_3(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[1].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_4(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = None
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_5(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(None)
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_6(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(None))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_7(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = None
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_8(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[1] = tmp_sorted
            self._balance_list(0)

    def xǁBarrelListǁsort__mutmut_9(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(None)

    def xǁBarrelListǁsort__mutmut_10(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(1)
    
    xǁBarrelListǁsort__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁsort__mutmut_1': xǁBarrelListǁsort__mutmut_1, 
        'xǁBarrelListǁsort__mutmut_2': xǁBarrelListǁsort__mutmut_2, 
        'xǁBarrelListǁsort__mutmut_3': xǁBarrelListǁsort__mutmut_3, 
        'xǁBarrelListǁsort__mutmut_4': xǁBarrelListǁsort__mutmut_4, 
        'xǁBarrelListǁsort__mutmut_5': xǁBarrelListǁsort__mutmut_5, 
        'xǁBarrelListǁsort__mutmut_6': xǁBarrelListǁsort__mutmut_6, 
        'xǁBarrelListǁsort__mutmut_7': xǁBarrelListǁsort__mutmut_7, 
        'xǁBarrelListǁsort__mutmut_8': xǁBarrelListǁsort__mutmut_8, 
        'xǁBarrelListǁsort__mutmut_9': xǁBarrelListǁsort__mutmut_9, 
        'xǁBarrelListǁsort__mutmut_10': xǁBarrelListǁsort__mutmut_10
    }
    
    def sort(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁsort__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁsort__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sort.__signature__ = _mutmut_signature(xǁBarrelListǁsort__mutmut_orig)
    xǁBarrelListǁsort__mutmut_orig.__name__ = 'xǁBarrelListǁsort'

    def reverse(self):
        for cur in self.lists:
            cur.reverse()
        self.lists.reverse()

    def xǁBarrelListǁcount__mutmut_orig(self, item):
        return sum([cur.count(item) for cur in self.lists])

    def xǁBarrelListǁcount__mutmut_1(self, item):
        return sum(None)

    def xǁBarrelListǁcount__mutmut_2(self, item):
        return sum([cur.count(None) for cur in self.lists])
    
    xǁBarrelListǁcount__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁcount__mutmut_1': xǁBarrelListǁcount__mutmut_1, 
        'xǁBarrelListǁcount__mutmut_2': xǁBarrelListǁcount__mutmut_2
    }
    
    def count(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁcount__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁcount__mutmut_mutants"), args, kwargs, self)
        return result 
    
    count.__signature__ = _mutmut_signature(xǁBarrelListǁcount__mutmut_orig)
    xǁBarrelListǁcount__mutmut_orig.__name__ = 'xǁBarrelListǁcount'

    def xǁBarrelListǁindex__mutmut_orig(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_1(self, item):
        len_accum = None
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_2(self, item):
        len_accum = 1
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_3(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = None
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_4(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(None)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_5(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.rindex(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_6(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum - rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_7(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum = len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_8(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum -= len(cur)
        raise ValueError(f'{item!r} is not in list')

    def xǁBarrelListǁindex__mutmut_9(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError(None)
    
    xǁBarrelListǁindex__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBarrelListǁindex__mutmut_1': xǁBarrelListǁindex__mutmut_1, 
        'xǁBarrelListǁindex__mutmut_2': xǁBarrelListǁindex__mutmut_2, 
        'xǁBarrelListǁindex__mutmut_3': xǁBarrelListǁindex__mutmut_3, 
        'xǁBarrelListǁindex__mutmut_4': xǁBarrelListǁindex__mutmut_4, 
        'xǁBarrelListǁindex__mutmut_5': xǁBarrelListǁindex__mutmut_5, 
        'xǁBarrelListǁindex__mutmut_6': xǁBarrelListǁindex__mutmut_6, 
        'xǁBarrelListǁindex__mutmut_7': xǁBarrelListǁindex__mutmut_7, 
        'xǁBarrelListǁindex__mutmut_8': xǁBarrelListǁindex__mutmut_8, 
        'xǁBarrelListǁindex__mutmut_9': xǁBarrelListǁindex__mutmut_9
    }
    
    def index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBarrelListǁindex__mutmut_orig"), object.__getattribute__(self, "xǁBarrelListǁindex__mutmut_mutants"), args, kwargs, self)
        return result 
    
    index.__signature__ = _mutmut_signature(xǁBarrelListǁindex__mutmut_orig)
    xǁBarrelListǁindex__mutmut_orig.__name__ = 'xǁBarrelListǁindex'


BList = BarrelList


class SplayList(list):
    """Like a `splay tree`_, the SplayList facilitates moving higher
    utility items closer to the front of the list for faster access.

    .. _splay tree: https://en.wikipedia.org/wiki/Splay_tree
    """

    def xǁSplayListǁshift__mutmut_orig(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, item)

    def xǁSplayListǁshift__mutmut_1(self, item_index, dest_index=1):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, item)

    def xǁSplayListǁshift__mutmut_2(self, item_index, dest_index=0):
        if item_index != dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, item)

    def xǁSplayListǁshift__mutmut_3(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = None
        self.insert(dest_index, item)

    def xǁSplayListǁshift__mutmut_4(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(None)
        self.insert(dest_index, item)

    def xǁSplayListǁshift__mutmut_5(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(None, item)

    def xǁSplayListǁshift__mutmut_6(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, None)

    def xǁSplayListǁshift__mutmut_7(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(item)

    def xǁSplayListǁshift__mutmut_8(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, )
    
    xǁSplayListǁshift__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSplayListǁshift__mutmut_1': xǁSplayListǁshift__mutmut_1, 
        'xǁSplayListǁshift__mutmut_2': xǁSplayListǁshift__mutmut_2, 
        'xǁSplayListǁshift__mutmut_3': xǁSplayListǁshift__mutmut_3, 
        'xǁSplayListǁshift__mutmut_4': xǁSplayListǁshift__mutmut_4, 
        'xǁSplayListǁshift__mutmut_5': xǁSplayListǁshift__mutmut_5, 
        'xǁSplayListǁshift__mutmut_6': xǁSplayListǁshift__mutmut_6, 
        'xǁSplayListǁshift__mutmut_7': xǁSplayListǁshift__mutmut_7, 
        'xǁSplayListǁshift__mutmut_8': xǁSplayListǁshift__mutmut_8
    }
    
    def shift(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSplayListǁshift__mutmut_orig"), object.__getattribute__(self, "xǁSplayListǁshift__mutmut_mutants"), args, kwargs, self)
        return result 
    
    shift.__signature__ = _mutmut_signature(xǁSplayListǁshift__mutmut_orig)
    xǁSplayListǁshift__mutmut_orig.__name__ = 'xǁSplayListǁshift'

    def xǁSplayListǁswap__mutmut_orig(self, item_index, dest_index):
        self[dest_index], self[item_index] = self[item_index], self[dest_index]

    def xǁSplayListǁswap__mutmut_1(self, item_index, dest_index):
        self[dest_index], self[item_index] = None
    
    xǁSplayListǁswap__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSplayListǁswap__mutmut_1': xǁSplayListǁswap__mutmut_1
    }
    
    def swap(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSplayListǁswap__mutmut_orig"), object.__getattribute__(self, "xǁSplayListǁswap__mutmut_mutants"), args, kwargs, self)
        return result 
    
    swap.__signature__ = _mutmut_signature(xǁSplayListǁswap__mutmut_orig)
    xǁSplayListǁswap__mutmut_orig.__name__ = 'xǁSplayListǁswap'
