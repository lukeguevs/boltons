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

"""\

The :class:`set` type brings the practical expressiveness of
set theory to Python. It has a very rich API overall, but lacks a
couple of fundamental features. For one, sets are not ordered. On top
of this, sets are not indexable, i.e, ``my_set[8]`` will raise an
:exc:`TypeError`. The :class:`IndexedSet` type remedies both of these
issues without compromising on the excellent complexity
characteristics of Python's built-in set implementation.
"""


from bisect import bisect_left
from collections.abc import MutableSet
from itertools import chain, islice
import operator

_MISSING = object()


__all__ = ['IndexedSet', 'complement']


_COMPACTION_FACTOR = 8
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

# TODO: inherit from set()
# TODO: .discard_many(), .remove_many()
# TODO: raise exception on non-set params?
# TODO: technically reverse operators should probably reverse the
# order of the 'other' inputs and put self last (to try and maintain
# insertion order)


class IndexedSet(MutableSet):
    """``IndexedSet`` is a :class:`collections.MutableSet` that maintains
    insertion order and uniqueness of inserted elements. It's a hybrid
    type, mostly like an OrderedSet, but also :class:`list`-like, in
    that it supports indexing and slicing.

    Args:
        other (iterable): An optional iterable used to initialize the set.

    >>> x = IndexedSet(list(range(4)) + list(range(8)))
    >>> x
    IndexedSet([0, 1, 2, 3, 4, 5, 6, 7])
    >>> x - set(range(2))
    IndexedSet([2, 3, 4, 5, 6, 7])
    >>> x[-1]
    7
    >>> fcr = IndexedSet('freecreditreport.com')
    >>> ''.join(fcr[:fcr.index('.')])
    'frecditpo'

    Standard set operators and interoperation with :class:`set` are
    all supported:

    >>> fcr & set('cash4gold.com')
    IndexedSet(['c', 'd', 'o', '.', 'm'])

    As you can see, the ``IndexedSet`` is almost like a ``UniqueList``,
    retaining only one copy of a given value, in the order it was
    first added. For the curious, the reason why IndexedSet does not
    support setting items based on index (i.e, ``__setitem__()``),
    consider the following dilemma::

      my_indexed_set = [A, B, C, D]
      my_indexed_set[2] = A

    At this point, a set requires only one *A*, but a :class:`list` would
    overwrite *C*. Overwriting *C* would change the length of the list,
    meaning that ``my_indexed_set[2]`` would not be *A*, as expected with a
    list, but rather *D*. So, no ``__setitem__()``.

    Otherwise, the API strives to be as complete a union of the
    :class:`list` and :class:`set` APIs as possible.
    """
    def xǁIndexedSetǁ__init____mutmut_orig(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_1(self, other=None):
        self.item_index_map = None
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_2(self, other=None):
        self.item_index_map = dict()
        self.item_list = None
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_3(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = None
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_4(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = None
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_5(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 1
        self._c_max_size = 0
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_6(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = None
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_7(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 1
        if other:
            self.update(other)
    def xǁIndexedSetǁ__init____mutmut_8(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        self._compactions = 0
        self._c_max_size = 0
        if other:
            self.update(None)
    
    xǁIndexedSetǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__init____mutmut_1': xǁIndexedSetǁ__init____mutmut_1, 
        'xǁIndexedSetǁ__init____mutmut_2': xǁIndexedSetǁ__init____mutmut_2, 
        'xǁIndexedSetǁ__init____mutmut_3': xǁIndexedSetǁ__init____mutmut_3, 
        'xǁIndexedSetǁ__init____mutmut_4': xǁIndexedSetǁ__init____mutmut_4, 
        'xǁIndexedSetǁ__init____mutmut_5': xǁIndexedSetǁ__init____mutmut_5, 
        'xǁIndexedSetǁ__init____mutmut_6': xǁIndexedSetǁ__init____mutmut_6, 
        'xǁIndexedSetǁ__init____mutmut_7': xǁIndexedSetǁ__init____mutmut_7, 
        'xǁIndexedSetǁ__init____mutmut_8': xǁIndexedSetǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__init____mutmut_orig)
    xǁIndexedSetǁ__init____mutmut_orig.__name__ = 'xǁIndexedSetǁ__init__'

    # internal functions
    @property
    def _dead_index_count(self):
        return len(self.item_list) - len(self.item_index_map)

    def xǁIndexedSetǁ_compact__mutmut_orig(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_1(self):
        if self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_2(self):
        if not self.dead_indices:
            return
        self._compactions = 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_3(self):
        if not self.dead_indices:
            return
        self._compactions -= 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_4(self):
        if not self.dead_indices:
            return
        self._compactions += 2
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_5(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = None
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_6(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = None
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_7(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = None
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_8(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(None, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_9(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, None)
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_10(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_11(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, )
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_12(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(None):
            items[i] = item
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_13(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = None
            index_map[item] = i
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_14(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = None
        del items[-dead_index_count:]
        del self.dead_indices[:]

    def xǁIndexedSetǁ_compact__mutmut_15(self):
        if not self.dead_indices:
            return
        self._compactions += 1
        dead_index_count = self._dead_index_count
        items, index_map = self.item_list, self.item_index_map
        self._c_max_size = max(self._c_max_size, len(items))
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[+dead_index_count:]
        del self.dead_indices[:]
    
    xǁIndexedSetǁ_compact__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ_compact__mutmut_1': xǁIndexedSetǁ_compact__mutmut_1, 
        'xǁIndexedSetǁ_compact__mutmut_2': xǁIndexedSetǁ_compact__mutmut_2, 
        'xǁIndexedSetǁ_compact__mutmut_3': xǁIndexedSetǁ_compact__mutmut_3, 
        'xǁIndexedSetǁ_compact__mutmut_4': xǁIndexedSetǁ_compact__mutmut_4, 
        'xǁIndexedSetǁ_compact__mutmut_5': xǁIndexedSetǁ_compact__mutmut_5, 
        'xǁIndexedSetǁ_compact__mutmut_6': xǁIndexedSetǁ_compact__mutmut_6, 
        'xǁIndexedSetǁ_compact__mutmut_7': xǁIndexedSetǁ_compact__mutmut_7, 
        'xǁIndexedSetǁ_compact__mutmut_8': xǁIndexedSetǁ_compact__mutmut_8, 
        'xǁIndexedSetǁ_compact__mutmut_9': xǁIndexedSetǁ_compact__mutmut_9, 
        'xǁIndexedSetǁ_compact__mutmut_10': xǁIndexedSetǁ_compact__mutmut_10, 
        'xǁIndexedSetǁ_compact__mutmut_11': xǁIndexedSetǁ_compact__mutmut_11, 
        'xǁIndexedSetǁ_compact__mutmut_12': xǁIndexedSetǁ_compact__mutmut_12, 
        'xǁIndexedSetǁ_compact__mutmut_13': xǁIndexedSetǁ_compact__mutmut_13, 
        'xǁIndexedSetǁ_compact__mutmut_14': xǁIndexedSetǁ_compact__mutmut_14, 
        'xǁIndexedSetǁ_compact__mutmut_15': xǁIndexedSetǁ_compact__mutmut_15
    }
    
    def _compact(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ_compact__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ_compact__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _compact.__signature__ = _mutmut_signature(xǁIndexedSetǁ_compact__mutmut_orig)
    xǁIndexedSetǁ_compact__mutmut_orig.__name__ = 'xǁIndexedSetǁ_compact'

    def xǁIndexedSetǁ_cull__mutmut_orig(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_1(self):
        ded = None
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_2(self):
        ded = self.dead_indices
        if ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_3(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = None
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_4(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_5(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) >= 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_6(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 385:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_7(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count >= (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_8(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) * _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_9(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[+1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_10(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-2] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_11(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is not _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_12(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = None
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_13(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 2
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_14(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[+(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_15(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead - 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_16(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 2)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_17(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is not _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_18(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead = 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_19(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead -= 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_20(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 2
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_21(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded or ded[-1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_22(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[+1][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_23(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-2][1] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_24(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][2] == len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_25(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] != len(items):
                del ded[-1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_26(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[+1]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_27(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-2]
            del items[-num_dead:]

    def xǁIndexedSetǁ_cull__mutmut_28(self):
        ded = self.dead_indices
        if not ded:
            return
        items, ii_map = self.item_list, self.item_index_map
        if not ii_map:
            del items[:]
            del ded[:]
        elif len(ded) > 384:
            self._compact()
        elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR):
            self._compact()
        elif items[-1] is _MISSING:  # get rid of dead right hand side
            num_dead = 1
            while items[-(num_dead + 1)] is _MISSING:
                num_dead += 1
            if ded and ded[-1][1] == len(items):
                del ded[-1]
            del items[+num_dead:]
    
    xǁIndexedSetǁ_cull__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ_cull__mutmut_1': xǁIndexedSetǁ_cull__mutmut_1, 
        'xǁIndexedSetǁ_cull__mutmut_2': xǁIndexedSetǁ_cull__mutmut_2, 
        'xǁIndexedSetǁ_cull__mutmut_3': xǁIndexedSetǁ_cull__mutmut_3, 
        'xǁIndexedSetǁ_cull__mutmut_4': xǁIndexedSetǁ_cull__mutmut_4, 
        'xǁIndexedSetǁ_cull__mutmut_5': xǁIndexedSetǁ_cull__mutmut_5, 
        'xǁIndexedSetǁ_cull__mutmut_6': xǁIndexedSetǁ_cull__mutmut_6, 
        'xǁIndexedSetǁ_cull__mutmut_7': xǁIndexedSetǁ_cull__mutmut_7, 
        'xǁIndexedSetǁ_cull__mutmut_8': xǁIndexedSetǁ_cull__mutmut_8, 
        'xǁIndexedSetǁ_cull__mutmut_9': xǁIndexedSetǁ_cull__mutmut_9, 
        'xǁIndexedSetǁ_cull__mutmut_10': xǁIndexedSetǁ_cull__mutmut_10, 
        'xǁIndexedSetǁ_cull__mutmut_11': xǁIndexedSetǁ_cull__mutmut_11, 
        'xǁIndexedSetǁ_cull__mutmut_12': xǁIndexedSetǁ_cull__mutmut_12, 
        'xǁIndexedSetǁ_cull__mutmut_13': xǁIndexedSetǁ_cull__mutmut_13, 
        'xǁIndexedSetǁ_cull__mutmut_14': xǁIndexedSetǁ_cull__mutmut_14, 
        'xǁIndexedSetǁ_cull__mutmut_15': xǁIndexedSetǁ_cull__mutmut_15, 
        'xǁIndexedSetǁ_cull__mutmut_16': xǁIndexedSetǁ_cull__mutmut_16, 
        'xǁIndexedSetǁ_cull__mutmut_17': xǁIndexedSetǁ_cull__mutmut_17, 
        'xǁIndexedSetǁ_cull__mutmut_18': xǁIndexedSetǁ_cull__mutmut_18, 
        'xǁIndexedSetǁ_cull__mutmut_19': xǁIndexedSetǁ_cull__mutmut_19, 
        'xǁIndexedSetǁ_cull__mutmut_20': xǁIndexedSetǁ_cull__mutmut_20, 
        'xǁIndexedSetǁ_cull__mutmut_21': xǁIndexedSetǁ_cull__mutmut_21, 
        'xǁIndexedSetǁ_cull__mutmut_22': xǁIndexedSetǁ_cull__mutmut_22, 
        'xǁIndexedSetǁ_cull__mutmut_23': xǁIndexedSetǁ_cull__mutmut_23, 
        'xǁIndexedSetǁ_cull__mutmut_24': xǁIndexedSetǁ_cull__mutmut_24, 
        'xǁIndexedSetǁ_cull__mutmut_25': xǁIndexedSetǁ_cull__mutmut_25, 
        'xǁIndexedSetǁ_cull__mutmut_26': xǁIndexedSetǁ_cull__mutmut_26, 
        'xǁIndexedSetǁ_cull__mutmut_27': xǁIndexedSetǁ_cull__mutmut_27, 
        'xǁIndexedSetǁ_cull__mutmut_28': xǁIndexedSetǁ_cull__mutmut_28
    }
    
    def _cull(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ_cull__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ_cull__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cull.__signature__ = _mutmut_signature(xǁIndexedSetǁ_cull__mutmut_orig)
    xǁIndexedSetǁ_cull__mutmut_orig.__name__ = 'xǁIndexedSetǁ_cull'

    def xǁIndexedSetǁ_get_real_index__mutmut_orig(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_1(self, index):
        if index <= 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_2(self, index):
        if index < 1:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_3(self, index):
        if index < 0:
            index = len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_4(self, index):
        if index < 0:
            index -= len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_5(self, index):
        if index < 0:
            index += len(self)
        if self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_6(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = None
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_7(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index <= d_start:
                break
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_8(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                return
            real_index += d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_9(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index = d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_10(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index -= d_stop - d_start
        return real_index

    def xǁIndexedSetǁ_get_real_index__mutmut_11(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        real_index = index
        for d_start, d_stop in self.dead_indices:
            if real_index < d_start:
                break
            real_index += d_stop + d_start
        return real_index
    
    xǁIndexedSetǁ_get_real_index__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ_get_real_index__mutmut_1': xǁIndexedSetǁ_get_real_index__mutmut_1, 
        'xǁIndexedSetǁ_get_real_index__mutmut_2': xǁIndexedSetǁ_get_real_index__mutmut_2, 
        'xǁIndexedSetǁ_get_real_index__mutmut_3': xǁIndexedSetǁ_get_real_index__mutmut_3, 
        'xǁIndexedSetǁ_get_real_index__mutmut_4': xǁIndexedSetǁ_get_real_index__mutmut_4, 
        'xǁIndexedSetǁ_get_real_index__mutmut_5': xǁIndexedSetǁ_get_real_index__mutmut_5, 
        'xǁIndexedSetǁ_get_real_index__mutmut_6': xǁIndexedSetǁ_get_real_index__mutmut_6, 
        'xǁIndexedSetǁ_get_real_index__mutmut_7': xǁIndexedSetǁ_get_real_index__mutmut_7, 
        'xǁIndexedSetǁ_get_real_index__mutmut_8': xǁIndexedSetǁ_get_real_index__mutmut_8, 
        'xǁIndexedSetǁ_get_real_index__mutmut_9': xǁIndexedSetǁ_get_real_index__mutmut_9, 
        'xǁIndexedSetǁ_get_real_index__mutmut_10': xǁIndexedSetǁ_get_real_index__mutmut_10, 
        'xǁIndexedSetǁ_get_real_index__mutmut_11': xǁIndexedSetǁ_get_real_index__mutmut_11
    }
    
    def _get_real_index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ_get_real_index__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ_get_real_index__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_real_index.__signature__ = _mutmut_signature(xǁIndexedSetǁ_get_real_index__mutmut_orig)
    xǁIndexedSetǁ_get_real_index__mutmut_orig.__name__ = 'xǁIndexedSetǁ_get_real_index'

    def xǁIndexedSetǁ_get_apparent_index__mutmut_orig(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_1(self, index):
        if index <= 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_2(self, index):
        if index < 1:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_3(self, index):
        if index < 0:
            index = len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_4(self, index):
        if index < 0:
            index -= len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_5(self, index):
        if index < 0:
            index += len(self)
        if self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_6(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = None
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_7(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index <= d_start:
                break
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_8(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                return
            apparent_index -= d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_9(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index = d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_10(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index += d_stop - d_start
        return apparent_index

    def xǁIndexedSetǁ_get_apparent_index__mutmut_11(self, index):
        if index < 0:
            index += len(self)
        if not self.dead_indices:
            return index
        apparent_index = index
        for d_start, d_stop in self.dead_indices:
            if index < d_start:
                break
            apparent_index -= d_stop + d_start
        return apparent_index
    
    xǁIndexedSetǁ_get_apparent_index__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ_get_apparent_index__mutmut_1': xǁIndexedSetǁ_get_apparent_index__mutmut_1, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_2': xǁIndexedSetǁ_get_apparent_index__mutmut_2, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_3': xǁIndexedSetǁ_get_apparent_index__mutmut_3, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_4': xǁIndexedSetǁ_get_apparent_index__mutmut_4, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_5': xǁIndexedSetǁ_get_apparent_index__mutmut_5, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_6': xǁIndexedSetǁ_get_apparent_index__mutmut_6, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_7': xǁIndexedSetǁ_get_apparent_index__mutmut_7, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_8': xǁIndexedSetǁ_get_apparent_index__mutmut_8, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_9': xǁIndexedSetǁ_get_apparent_index__mutmut_9, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_10': xǁIndexedSetǁ_get_apparent_index__mutmut_10, 
        'xǁIndexedSetǁ_get_apparent_index__mutmut_11': xǁIndexedSetǁ_get_apparent_index__mutmut_11
    }
    
    def _get_apparent_index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ_get_apparent_index__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ_get_apparent_index__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_apparent_index.__signature__ = _mutmut_signature(xǁIndexedSetǁ_get_apparent_index__mutmut_orig)
    xǁIndexedSetǁ_get_apparent_index__mutmut_orig.__name__ = 'xǁIndexedSetǁ_get_apparent_index'

    def xǁIndexedSetǁ_add_dead__mutmut_orig(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_1(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = None
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_2(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is not None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_3(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = None
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_4(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start - 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_5(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 2
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_6(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = None
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_7(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_8(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(None)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_9(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = None
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_10(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(None, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_11(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, None)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_12(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_13(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, )
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_14(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = None
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_15(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx + 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_16(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 2]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_17(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = None
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_18(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start < d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_19(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start < stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_20(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = None
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_21(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[1] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_22(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start < d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_23(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop < stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_24(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = None
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_25(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[2] = stop
        else:
            dints.insert(int_idx, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_26(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(None, cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_27(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, None)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_28(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(cand_int)
        return

    def xǁIndexedSetǁ_add_dead__mutmut_29(self, start, stop=None):
        # TODO: does not handle when the new interval subsumes
        # multiple existing intervals
        dints = self.dead_indices
        if stop is None:
            stop = start + 1
        cand_int = [start, stop]
        if not dints:
            dints.append(cand_int)
            return
        int_idx = bisect_left(dints, cand_int)
        dint = dints[int_idx - 1]
        d_start, d_stop = dint
        if start <= d_start <= stop:
            dint[0] = start
        elif start <= d_stop <= stop:
            dint[1] = stop
        else:
            dints.insert(int_idx, )
        return
    
    xǁIndexedSetǁ_add_dead__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ_add_dead__mutmut_1': xǁIndexedSetǁ_add_dead__mutmut_1, 
        'xǁIndexedSetǁ_add_dead__mutmut_2': xǁIndexedSetǁ_add_dead__mutmut_2, 
        'xǁIndexedSetǁ_add_dead__mutmut_3': xǁIndexedSetǁ_add_dead__mutmut_3, 
        'xǁIndexedSetǁ_add_dead__mutmut_4': xǁIndexedSetǁ_add_dead__mutmut_4, 
        'xǁIndexedSetǁ_add_dead__mutmut_5': xǁIndexedSetǁ_add_dead__mutmut_5, 
        'xǁIndexedSetǁ_add_dead__mutmut_6': xǁIndexedSetǁ_add_dead__mutmut_6, 
        'xǁIndexedSetǁ_add_dead__mutmut_7': xǁIndexedSetǁ_add_dead__mutmut_7, 
        'xǁIndexedSetǁ_add_dead__mutmut_8': xǁIndexedSetǁ_add_dead__mutmut_8, 
        'xǁIndexedSetǁ_add_dead__mutmut_9': xǁIndexedSetǁ_add_dead__mutmut_9, 
        'xǁIndexedSetǁ_add_dead__mutmut_10': xǁIndexedSetǁ_add_dead__mutmut_10, 
        'xǁIndexedSetǁ_add_dead__mutmut_11': xǁIndexedSetǁ_add_dead__mutmut_11, 
        'xǁIndexedSetǁ_add_dead__mutmut_12': xǁIndexedSetǁ_add_dead__mutmut_12, 
        'xǁIndexedSetǁ_add_dead__mutmut_13': xǁIndexedSetǁ_add_dead__mutmut_13, 
        'xǁIndexedSetǁ_add_dead__mutmut_14': xǁIndexedSetǁ_add_dead__mutmut_14, 
        'xǁIndexedSetǁ_add_dead__mutmut_15': xǁIndexedSetǁ_add_dead__mutmut_15, 
        'xǁIndexedSetǁ_add_dead__mutmut_16': xǁIndexedSetǁ_add_dead__mutmut_16, 
        'xǁIndexedSetǁ_add_dead__mutmut_17': xǁIndexedSetǁ_add_dead__mutmut_17, 
        'xǁIndexedSetǁ_add_dead__mutmut_18': xǁIndexedSetǁ_add_dead__mutmut_18, 
        'xǁIndexedSetǁ_add_dead__mutmut_19': xǁIndexedSetǁ_add_dead__mutmut_19, 
        'xǁIndexedSetǁ_add_dead__mutmut_20': xǁIndexedSetǁ_add_dead__mutmut_20, 
        'xǁIndexedSetǁ_add_dead__mutmut_21': xǁIndexedSetǁ_add_dead__mutmut_21, 
        'xǁIndexedSetǁ_add_dead__mutmut_22': xǁIndexedSetǁ_add_dead__mutmut_22, 
        'xǁIndexedSetǁ_add_dead__mutmut_23': xǁIndexedSetǁ_add_dead__mutmut_23, 
        'xǁIndexedSetǁ_add_dead__mutmut_24': xǁIndexedSetǁ_add_dead__mutmut_24, 
        'xǁIndexedSetǁ_add_dead__mutmut_25': xǁIndexedSetǁ_add_dead__mutmut_25, 
        'xǁIndexedSetǁ_add_dead__mutmut_26': xǁIndexedSetǁ_add_dead__mutmut_26, 
        'xǁIndexedSetǁ_add_dead__mutmut_27': xǁIndexedSetǁ_add_dead__mutmut_27, 
        'xǁIndexedSetǁ_add_dead__mutmut_28': xǁIndexedSetǁ_add_dead__mutmut_28, 
        'xǁIndexedSetǁ_add_dead__mutmut_29': xǁIndexedSetǁ_add_dead__mutmut_29
    }
    
    def _add_dead(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ_add_dead__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ_add_dead__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _add_dead.__signature__ = _mutmut_signature(xǁIndexedSetǁ_add_dead__mutmut_orig)
    xǁIndexedSetǁ_add_dead__mutmut_orig.__name__ = 'xǁIndexedSetǁ_add_dead'

    # common operations (shared by set and list)
    def __len__(self):
        return len(self.item_index_map)

    def xǁIndexedSetǁ__contains____mutmut_orig(self, item):
        return item in self.item_index_map

    def xǁIndexedSetǁ__contains____mutmut_1(self, item):
        return item not in self.item_index_map
    
    xǁIndexedSetǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__contains____mutmut_1': xǁIndexedSetǁ__contains____mutmut_1
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__contains____mutmut_orig)
    xǁIndexedSetǁ__contains____mutmut_orig.__name__ = 'xǁIndexedSetǁ__contains__'

    def xǁIndexedSetǁ__iter____mutmut_orig(self):
        return (item for item in self.item_list if item is not _MISSING)

    def xǁIndexedSetǁ__iter____mutmut_1(self):
        return (item for item in self.item_list if item is _MISSING)
    
    xǁIndexedSetǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__iter____mutmut_1': xǁIndexedSetǁ__iter____mutmut_1
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__iter____mutmut_orig)
    xǁIndexedSetǁ__iter____mutmut_orig.__name__ = 'xǁIndexedSetǁ__iter__'

    def xǁIndexedSetǁ__reversed____mutmut_orig(self):
        item_list = self.item_list
        return (item for item in reversed(item_list) if item is not _MISSING)

    def xǁIndexedSetǁ__reversed____mutmut_1(self):
        item_list = None
        return (item for item in reversed(item_list) if item is not _MISSING)

    def xǁIndexedSetǁ__reversed____mutmut_2(self):
        item_list = self.item_list
        return (item for item in reversed(None) if item is not _MISSING)

    def xǁIndexedSetǁ__reversed____mutmut_3(self):
        item_list = self.item_list
        return (item for item in reversed(item_list) if item is _MISSING)
    
    xǁIndexedSetǁ__reversed____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__reversed____mutmut_1': xǁIndexedSetǁ__reversed____mutmut_1, 
        'xǁIndexedSetǁ__reversed____mutmut_2': xǁIndexedSetǁ__reversed____mutmut_2, 
        'xǁIndexedSetǁ__reversed____mutmut_3': xǁIndexedSetǁ__reversed____mutmut_3
    }
    
    def __reversed__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__reversed____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__reversed____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __reversed__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__reversed____mutmut_orig)
    xǁIndexedSetǁ__reversed____mutmut_orig.__name__ = 'xǁIndexedSetǁ__reversed__'

    def xǁIndexedSetǁ__repr____mutmut_orig(self):
        return f'{self.__class__.__name__}({list(self)!r})'

    def xǁIndexedSetǁ__repr____mutmut_1(self):
        return f'{self.__class__.__name__}({list(None)!r})'
    
    xǁIndexedSetǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__repr____mutmut_1': xǁIndexedSetǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__repr____mutmut_orig)
    xǁIndexedSetǁ__repr____mutmut_orig.__name__ = 'xǁIndexedSetǁ__repr__'

    def xǁIndexedSetǁ__eq____mutmut_orig(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_1(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) or list(self) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_2(self, other):
        if isinstance(other, IndexedSet):
            return len(self) != len(other) and list(self) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_3(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(None) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_4(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) != list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_5(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(None)
        try:
            return set(self) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_6(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(None) == set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_7(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(self) != set(other)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_8(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(self) == set(None)
        except TypeError:
            return False

    def xǁIndexedSetǁ__eq____mutmut_9(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        try:
            return set(self) == set(other)
        except TypeError:
            return True
    
    xǁIndexedSetǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__eq____mutmut_1': xǁIndexedSetǁ__eq____mutmut_1, 
        'xǁIndexedSetǁ__eq____mutmut_2': xǁIndexedSetǁ__eq____mutmut_2, 
        'xǁIndexedSetǁ__eq____mutmut_3': xǁIndexedSetǁ__eq____mutmut_3, 
        'xǁIndexedSetǁ__eq____mutmut_4': xǁIndexedSetǁ__eq____mutmut_4, 
        'xǁIndexedSetǁ__eq____mutmut_5': xǁIndexedSetǁ__eq____mutmut_5, 
        'xǁIndexedSetǁ__eq____mutmut_6': xǁIndexedSetǁ__eq____mutmut_6, 
        'xǁIndexedSetǁ__eq____mutmut_7': xǁIndexedSetǁ__eq____mutmut_7, 
        'xǁIndexedSetǁ__eq____mutmut_8': xǁIndexedSetǁ__eq____mutmut_8, 
        'xǁIndexedSetǁ__eq____mutmut_9': xǁIndexedSetǁ__eq____mutmut_9
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__eq____mutmut_orig)
    xǁIndexedSetǁ__eq____mutmut_orig.__name__ = 'xǁIndexedSetǁ__eq__'

    @classmethod
    def from_iterable(cls, it):
        "from_iterable(it) -> create a set from an iterable"
        return cls(it)

    # set operations
    def xǁIndexedSetǁadd__mutmut_orig(self, item):
        "add(item) -> add item to the set"
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    # set operations
    def xǁIndexedSetǁadd__mutmut_1(self, item):
        "XXadd(item) -> add item to the setXX"
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    # set operations
    def xǁIndexedSetǁadd__mutmut_2(self, item):
        "ADD(ITEM) -> ADD ITEM TO THE SET"
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    # set operations
    def xǁIndexedSetǁadd__mutmut_3(self, item):
        "add(item) -> add item to the set"
        if item in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    # set operations
    def xǁIndexedSetǁadd__mutmut_4(self, item):
        "add(item) -> add item to the set"
        if item not in self.item_index_map:
            self.item_index_map[item] = None
            self.item_list.append(item)

    # set operations
    def xǁIndexedSetǁadd__mutmut_5(self, item):
        "add(item) -> add item to the set"
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(None)
    
    xǁIndexedSetǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁadd__mutmut_1': xǁIndexedSetǁadd__mutmut_1, 
        'xǁIndexedSetǁadd__mutmut_2': xǁIndexedSetǁadd__mutmut_2, 
        'xǁIndexedSetǁadd__mutmut_3': xǁIndexedSetǁadd__mutmut_3, 
        'xǁIndexedSetǁadd__mutmut_4': xǁIndexedSetǁadd__mutmut_4, 
        'xǁIndexedSetǁadd__mutmut_5': xǁIndexedSetǁadd__mutmut_5
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁadd__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁIndexedSetǁadd__mutmut_orig)
    xǁIndexedSetǁadd__mutmut_orig.__name__ = 'xǁIndexedSetǁadd'

    def xǁIndexedSetǁremove__mutmut_orig(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_1(self, item):
        "XXremove(item) -> remove item from the set, raises if not presentXX"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_2(self, item):
        "REMOVE(ITEM) -> REMOVE ITEM FROM THE SET, RAISES IF NOT PRESENT"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_3(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = None
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_4(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(None)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_5(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(None)
        self.item_list[didx] = _MISSING
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_6(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = None
        self._add_dead(didx)
        self._cull()

    def xǁIndexedSetǁremove__mutmut_7(self, item):
        "remove(item) -> remove item from the set, raises if not present"
        try:
            didx = self.item_index_map.pop(item)
        except KeyError:
            raise KeyError(item)
        self.item_list[didx] = _MISSING
        self._add_dead(None)
        self._cull()
    
    xǁIndexedSetǁremove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁremove__mutmut_1': xǁIndexedSetǁremove__mutmut_1, 
        'xǁIndexedSetǁremove__mutmut_2': xǁIndexedSetǁremove__mutmut_2, 
        'xǁIndexedSetǁremove__mutmut_3': xǁIndexedSetǁremove__mutmut_3, 
        'xǁIndexedSetǁremove__mutmut_4': xǁIndexedSetǁremove__mutmut_4, 
        'xǁIndexedSetǁremove__mutmut_5': xǁIndexedSetǁremove__mutmut_5, 
        'xǁIndexedSetǁremove__mutmut_6': xǁIndexedSetǁremove__mutmut_6, 
        'xǁIndexedSetǁremove__mutmut_7': xǁIndexedSetǁremove__mutmut_7
    }
    
    def remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁremove__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁremove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    remove.__signature__ = _mutmut_signature(xǁIndexedSetǁremove__mutmut_orig)
    xǁIndexedSetǁremove__mutmut_orig.__name__ = 'xǁIndexedSetǁremove'

    def xǁIndexedSetǁdiscard__mutmut_orig(self, item):
        "discard(item) -> discard item from the set (does not raise)"
        try:
            self.remove(item)
        except KeyError:
            pass

    def xǁIndexedSetǁdiscard__mutmut_1(self, item):
        "XXdiscard(item) -> discard item from the set (does not raise)XX"
        try:
            self.remove(item)
        except KeyError:
            pass

    def xǁIndexedSetǁdiscard__mutmut_2(self, item):
        "DISCARD(ITEM) -> DISCARD ITEM FROM THE SET (DOES NOT RAISE)"
        try:
            self.remove(item)
        except KeyError:
            pass

    def xǁIndexedSetǁdiscard__mutmut_3(self, item):
        "discard(item) -> discard item from the set (does not raise)"
        try:
            self.remove(None)
        except KeyError:
            pass
    
    xǁIndexedSetǁdiscard__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁdiscard__mutmut_1': xǁIndexedSetǁdiscard__mutmut_1, 
        'xǁIndexedSetǁdiscard__mutmut_2': xǁIndexedSetǁdiscard__mutmut_2, 
        'xǁIndexedSetǁdiscard__mutmut_3': xǁIndexedSetǁdiscard__mutmut_3
    }
    
    def discard(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁdiscard__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁdiscard__mutmut_mutants"), args, kwargs, self)
        return result 
    
    discard.__signature__ = _mutmut_signature(xǁIndexedSetǁdiscard__mutmut_orig)
    xǁIndexedSetǁdiscard__mutmut_orig.__name__ = 'xǁIndexedSetǁdiscard'

    def xǁIndexedSetǁclear__mutmut_orig(self):
        "clear() -> empty the set"
        del self.item_list[:]
        del self.dead_indices[:]
        self.item_index_map.clear()

    def xǁIndexedSetǁclear__mutmut_1(self):
        "XXclear() -> empty the setXX"
        del self.item_list[:]
        del self.dead_indices[:]
        self.item_index_map.clear()

    def xǁIndexedSetǁclear__mutmut_2(self):
        "CLEAR() -> EMPTY THE SET"
        del self.item_list[:]
        del self.dead_indices[:]
        self.item_index_map.clear()
    
    xǁIndexedSetǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁclear__mutmut_1': xǁIndexedSetǁclear__mutmut_1, 
        'xǁIndexedSetǁclear__mutmut_2': xǁIndexedSetǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁclear__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁIndexedSetǁclear__mutmut_orig)
    xǁIndexedSetǁclear__mutmut_orig.__name__ = 'xǁIndexedSetǁclear'

    def xǁIndexedSetǁisdisjoint__mutmut_orig(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_1(self, other):
        "XXisdisjoint(other) -> return True if no overlap with otherXX"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_2(self, other):
        "isdisjoint(other) -> return true if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_3(self, other):
        "ISDISJOINT(OTHER) -> RETURN TRUE IF NO OVERLAP WITH OTHER"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_4(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = None
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_5(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_6(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return True
        return True

    def xǁIndexedSetǁisdisjoint__mutmut_7(self, other):
        "isdisjoint(other) -> return True if no overlap with other"
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return False
    
    xǁIndexedSetǁisdisjoint__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁisdisjoint__mutmut_1': xǁIndexedSetǁisdisjoint__mutmut_1, 
        'xǁIndexedSetǁisdisjoint__mutmut_2': xǁIndexedSetǁisdisjoint__mutmut_2, 
        'xǁIndexedSetǁisdisjoint__mutmut_3': xǁIndexedSetǁisdisjoint__mutmut_3, 
        'xǁIndexedSetǁisdisjoint__mutmut_4': xǁIndexedSetǁisdisjoint__mutmut_4, 
        'xǁIndexedSetǁisdisjoint__mutmut_5': xǁIndexedSetǁisdisjoint__mutmut_5, 
        'xǁIndexedSetǁisdisjoint__mutmut_6': xǁIndexedSetǁisdisjoint__mutmut_6, 
        'xǁIndexedSetǁisdisjoint__mutmut_7': xǁIndexedSetǁisdisjoint__mutmut_7
    }
    
    def isdisjoint(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁisdisjoint__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁisdisjoint__mutmut_mutants"), args, kwargs, self)
        return result 
    
    isdisjoint.__signature__ = _mutmut_signature(xǁIndexedSetǁisdisjoint__mutmut_orig)
    xǁIndexedSetǁisdisjoint__mutmut_orig.__name__ = 'xǁIndexedSetǁisdisjoint'

    def xǁIndexedSetǁissubset__mutmut_orig(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_1(self, other):
        "XXissubset(other) -> return True if other contains this setXX"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_2(self, other):
        "issubset(other) -> return true if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_3(self, other):
        "ISSUBSET(OTHER) -> RETURN TRUE IF OTHER CONTAINS THIS SET"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_4(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) <= len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_5(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return True
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_6(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k in other:
                return False
        return True

    def xǁIndexedSetǁissubset__mutmut_7(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return True
        return True

    def xǁIndexedSetǁissubset__mutmut_8(self, other):
        "issubset(other) -> return True if other contains this set"
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return False
    
    xǁIndexedSetǁissubset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁissubset__mutmut_1': xǁIndexedSetǁissubset__mutmut_1, 
        'xǁIndexedSetǁissubset__mutmut_2': xǁIndexedSetǁissubset__mutmut_2, 
        'xǁIndexedSetǁissubset__mutmut_3': xǁIndexedSetǁissubset__mutmut_3, 
        'xǁIndexedSetǁissubset__mutmut_4': xǁIndexedSetǁissubset__mutmut_4, 
        'xǁIndexedSetǁissubset__mutmut_5': xǁIndexedSetǁissubset__mutmut_5, 
        'xǁIndexedSetǁissubset__mutmut_6': xǁIndexedSetǁissubset__mutmut_6, 
        'xǁIndexedSetǁissubset__mutmut_7': xǁIndexedSetǁissubset__mutmut_7, 
        'xǁIndexedSetǁissubset__mutmut_8': xǁIndexedSetǁissubset__mutmut_8
    }
    
    def issubset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁissubset__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁissubset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    issubset.__signature__ = _mutmut_signature(xǁIndexedSetǁissubset__mutmut_orig)
    xǁIndexedSetǁissubset__mutmut_orig.__name__ = 'xǁIndexedSetǁissubset'

    def xǁIndexedSetǁissuperset__mutmut_orig(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_1(self, other):
        "XXissuperset(other) -> return True if set contains otherXX"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_2(self, other):
        "issuperset(other) -> return true if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_3(self, other):
        "ISSUPERSET(OTHER) -> RETURN TRUE IF SET CONTAINS OTHER"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_4(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) >= len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_5(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return True
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_6(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = None
        for k in other:
            if k not in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_7(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def xǁIndexedSetǁissuperset__mutmut_8(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return True
        return True

    def xǁIndexedSetǁissuperset__mutmut_9(self, other):
        "issuperset(other) -> return True if set contains other"
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return False
    
    xǁIndexedSetǁissuperset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁissuperset__mutmut_1': xǁIndexedSetǁissuperset__mutmut_1, 
        'xǁIndexedSetǁissuperset__mutmut_2': xǁIndexedSetǁissuperset__mutmut_2, 
        'xǁIndexedSetǁissuperset__mutmut_3': xǁIndexedSetǁissuperset__mutmut_3, 
        'xǁIndexedSetǁissuperset__mutmut_4': xǁIndexedSetǁissuperset__mutmut_4, 
        'xǁIndexedSetǁissuperset__mutmut_5': xǁIndexedSetǁissuperset__mutmut_5, 
        'xǁIndexedSetǁissuperset__mutmut_6': xǁIndexedSetǁissuperset__mutmut_6, 
        'xǁIndexedSetǁissuperset__mutmut_7': xǁIndexedSetǁissuperset__mutmut_7, 
        'xǁIndexedSetǁissuperset__mutmut_8': xǁIndexedSetǁissuperset__mutmut_8, 
        'xǁIndexedSetǁissuperset__mutmut_9': xǁIndexedSetǁissuperset__mutmut_9
    }
    
    def issuperset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁissuperset__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁissuperset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    issuperset.__signature__ = _mutmut_signature(xǁIndexedSetǁissuperset__mutmut_orig)
    xǁIndexedSetǁissuperset__mutmut_orig.__name__ = 'xǁIndexedSetǁissuperset'

    def xǁIndexedSetǁunion__mutmut_orig(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(chain(self, *others))

    def xǁIndexedSetǁunion__mutmut_1(self, *others):
        "XXunion(*others) -> return a new set containing this set and othersXX"
        return self.from_iterable(chain(self, *others))

    def xǁIndexedSetǁunion__mutmut_2(self, *others):
        "UNION(*OTHERS) -> RETURN A NEW SET CONTAINING THIS SET AND OTHERS"
        return self.from_iterable(chain(self, *others))

    def xǁIndexedSetǁunion__mutmut_3(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(None)

    def xǁIndexedSetǁunion__mutmut_4(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(chain(None, *others))

    def xǁIndexedSetǁunion__mutmut_5(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(chain(*others))

    def xǁIndexedSetǁunion__mutmut_6(self, *others):
        "union(*others) -> return a new set containing this set and others"
        return self.from_iterable(chain(self, ))
    
    xǁIndexedSetǁunion__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁunion__mutmut_1': xǁIndexedSetǁunion__mutmut_1, 
        'xǁIndexedSetǁunion__mutmut_2': xǁIndexedSetǁunion__mutmut_2, 
        'xǁIndexedSetǁunion__mutmut_3': xǁIndexedSetǁunion__mutmut_3, 
        'xǁIndexedSetǁunion__mutmut_4': xǁIndexedSetǁunion__mutmut_4, 
        'xǁIndexedSetǁunion__mutmut_5': xǁIndexedSetǁunion__mutmut_5, 
        'xǁIndexedSetǁunion__mutmut_6': xǁIndexedSetǁunion__mutmut_6
    }
    
    def union(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁunion__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁunion__mutmut_mutants"), args, kwargs, self)
        return result 
    
    union.__signature__ = _mutmut_signature(xǁIndexedSetǁunion__mutmut_orig)
    xǁIndexedSetǁunion__mutmut_orig.__name__ = 'xǁIndexedSetǁunion'

    def xǁIndexedSetǁiter_intersection__mutmut_orig(self, *others):
        "iter_intersection(*others) -> iterate over elements also in others"
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_intersection__mutmut_1(self, *others):
        "XXiter_intersection(*others) -> iterate over elements also in othersXX"
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_intersection__mutmut_2(self, *others):
        "ITER_INTERSECTION(*OTHERS) -> ITERATE OVER ELEMENTS ALSO IN OTHERS"
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_intersection__mutmut_3(self, *others):
        "iter_intersection(*others) -> iterate over elements also in others"
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_intersection__mutmut_4(self, *others):
        "iter_intersection(*others) -> iterate over elements also in others"
        for k in self:
            for other in others:
                if k not in other:
                    return
            else:
                yield k
        return
    
    xǁIndexedSetǁiter_intersection__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁiter_intersection__mutmut_1': xǁIndexedSetǁiter_intersection__mutmut_1, 
        'xǁIndexedSetǁiter_intersection__mutmut_2': xǁIndexedSetǁiter_intersection__mutmut_2, 
        'xǁIndexedSetǁiter_intersection__mutmut_3': xǁIndexedSetǁiter_intersection__mutmut_3, 
        'xǁIndexedSetǁiter_intersection__mutmut_4': xǁIndexedSetǁiter_intersection__mutmut_4
    }
    
    def iter_intersection(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁiter_intersection__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁiter_intersection__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iter_intersection.__signature__ = _mutmut_signature(xǁIndexedSetǁiter_intersection__mutmut_orig)
    xǁIndexedSetǁiter_intersection__mutmut_orig.__name__ = 'xǁIndexedSetǁiter_intersection'

    def xǁIndexedSetǁintersection__mutmut_orig(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_1(self, *others):
        "XXintersection(*others) -> get a set with overlap of this and othersXX"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_2(self, *others):
        "INTERSECTION(*OTHERS) -> GET A SET WITH OVERLAP OF THIS AND OTHERS"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_3(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) != 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_4(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 2:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_5(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = None
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_6(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[1]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_7(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(None)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_8(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_intersection(*others))

    def xǁIndexedSetǁintersection__mutmut_9(self, *others):
        "intersection(*others) -> get a set with overlap of this and others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(None)
    
    xǁIndexedSetǁintersection__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁintersection__mutmut_1': xǁIndexedSetǁintersection__mutmut_1, 
        'xǁIndexedSetǁintersection__mutmut_2': xǁIndexedSetǁintersection__mutmut_2, 
        'xǁIndexedSetǁintersection__mutmut_3': xǁIndexedSetǁintersection__mutmut_3, 
        'xǁIndexedSetǁintersection__mutmut_4': xǁIndexedSetǁintersection__mutmut_4, 
        'xǁIndexedSetǁintersection__mutmut_5': xǁIndexedSetǁintersection__mutmut_5, 
        'xǁIndexedSetǁintersection__mutmut_6': xǁIndexedSetǁintersection__mutmut_6, 
        'xǁIndexedSetǁintersection__mutmut_7': xǁIndexedSetǁintersection__mutmut_7, 
        'xǁIndexedSetǁintersection__mutmut_8': xǁIndexedSetǁintersection__mutmut_8, 
        'xǁIndexedSetǁintersection__mutmut_9': xǁIndexedSetǁintersection__mutmut_9
    }
    
    def intersection(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁintersection__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁintersection__mutmut_mutants"), args, kwargs, self)
        return result 
    
    intersection.__signature__ = _mutmut_signature(xǁIndexedSetǁintersection__mutmut_orig)
    xǁIndexedSetǁintersection__mutmut_orig.__name__ = 'xǁIndexedSetǁintersection'

    def xǁIndexedSetǁiter_difference__mutmut_orig(self, *others):
        "iter_difference(*others) -> iterate over elements not in others"
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_difference__mutmut_1(self, *others):
        "XXiter_difference(*others) -> iterate over elements not in othersXX"
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_difference__mutmut_2(self, *others):
        "ITER_DIFFERENCE(*OTHERS) -> ITERATE OVER ELEMENTS NOT IN OTHERS"
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_difference__mutmut_3(self, *others):
        "iter_difference(*others) -> iterate over elements not in others"
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def xǁIndexedSetǁiter_difference__mutmut_4(self, *others):
        "iter_difference(*others) -> iterate over elements not in others"
        for k in self:
            for other in others:
                if k in other:
                    return
            else:
                yield k
        return
    
    xǁIndexedSetǁiter_difference__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁiter_difference__mutmut_1': xǁIndexedSetǁiter_difference__mutmut_1, 
        'xǁIndexedSetǁiter_difference__mutmut_2': xǁIndexedSetǁiter_difference__mutmut_2, 
        'xǁIndexedSetǁiter_difference__mutmut_3': xǁIndexedSetǁiter_difference__mutmut_3, 
        'xǁIndexedSetǁiter_difference__mutmut_4': xǁIndexedSetǁiter_difference__mutmut_4
    }
    
    def iter_difference(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁiter_difference__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁiter_difference__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iter_difference.__signature__ = _mutmut_signature(xǁIndexedSetǁiter_difference__mutmut_orig)
    xǁIndexedSetǁiter_difference__mutmut_orig.__name__ = 'xǁIndexedSetǁiter_difference'

    def xǁIndexedSetǁdifference__mutmut_orig(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_1(self, *others):
        "XXdifference(*others) -> get a new set with elements not in othersXX"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_2(self, *others):
        "DIFFERENCE(*OTHERS) -> GET A NEW SET WITH ELEMENTS NOT IN OTHERS"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_3(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) != 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_4(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 2:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_5(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = None
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_6(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[1]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_7(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(None)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_8(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k in other)
        return self.from_iterable(self.iter_difference(*others))

    def xǁIndexedSetǁdifference__mutmut_9(self, *others):
        "difference(*others) -> get a new set with elements not in others"
        if len(others) == 1:
            other = others[0]
            return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(None)
    
    xǁIndexedSetǁdifference__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁdifference__mutmut_1': xǁIndexedSetǁdifference__mutmut_1, 
        'xǁIndexedSetǁdifference__mutmut_2': xǁIndexedSetǁdifference__mutmut_2, 
        'xǁIndexedSetǁdifference__mutmut_3': xǁIndexedSetǁdifference__mutmut_3, 
        'xǁIndexedSetǁdifference__mutmut_4': xǁIndexedSetǁdifference__mutmut_4, 
        'xǁIndexedSetǁdifference__mutmut_5': xǁIndexedSetǁdifference__mutmut_5, 
        'xǁIndexedSetǁdifference__mutmut_6': xǁIndexedSetǁdifference__mutmut_6, 
        'xǁIndexedSetǁdifference__mutmut_7': xǁIndexedSetǁdifference__mutmut_7, 
        'xǁIndexedSetǁdifference__mutmut_8': xǁIndexedSetǁdifference__mutmut_8, 
        'xǁIndexedSetǁdifference__mutmut_9': xǁIndexedSetǁdifference__mutmut_9
    }
    
    def difference(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁdifference__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁdifference__mutmut_mutants"), args, kwargs, self)
        return result 
    
    difference.__signature__ = _mutmut_signature(xǁIndexedSetǁdifference__mutmut_orig)
    xǁIndexedSetǁdifference__mutmut_orig.__name__ = 'xǁIndexedSetǁdifference'

    def xǁIndexedSetǁsymmetric_difference__mutmut_orig(self, *others):
        "symmetric_difference(*others) -> XOR set of this and others"
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    def xǁIndexedSetǁsymmetric_difference__mutmut_1(self, *others):
        "XXsymmetric_difference(*others) -> XOR set of this and othersXX"
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    def xǁIndexedSetǁsymmetric_difference__mutmut_2(self, *others):
        "symmetric_difference(*others) -> xor set of this and others"
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    def xǁIndexedSetǁsymmetric_difference__mutmut_3(self, *others):
        "SYMMETRIC_DIFFERENCE(*OTHERS) -> XOR SET OF THIS AND OTHERS"
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    def xǁIndexedSetǁsymmetric_difference__mutmut_4(self, *others):
        "symmetric_difference(*others) -> XOR set of this and others"
        ret = None
        return ret.difference(self.intersection(*others))

    def xǁIndexedSetǁsymmetric_difference__mutmut_5(self, *others):
        "symmetric_difference(*others) -> XOR set of this and others"
        ret = self.union(*others)
        return ret.difference(None)
    
    xǁIndexedSetǁsymmetric_difference__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁsymmetric_difference__mutmut_1': xǁIndexedSetǁsymmetric_difference__mutmut_1, 
        'xǁIndexedSetǁsymmetric_difference__mutmut_2': xǁIndexedSetǁsymmetric_difference__mutmut_2, 
        'xǁIndexedSetǁsymmetric_difference__mutmut_3': xǁIndexedSetǁsymmetric_difference__mutmut_3, 
        'xǁIndexedSetǁsymmetric_difference__mutmut_4': xǁIndexedSetǁsymmetric_difference__mutmut_4, 
        'xǁIndexedSetǁsymmetric_difference__mutmut_5': xǁIndexedSetǁsymmetric_difference__mutmut_5
    }
    
    def symmetric_difference(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁsymmetric_difference__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁsymmetric_difference__mutmut_mutants"), args, kwargs, self)
        return result 
    
    symmetric_difference.__signature__ = _mutmut_signature(xǁIndexedSetǁsymmetric_difference__mutmut_orig)
    xǁIndexedSetǁsymmetric_difference__mutmut_orig.__name__ = 'xǁIndexedSetǁsymmetric_difference'

    __or__  = __ror__  = union
    __and__ = __rand__ = intersection
    __sub__ = difference
    __xor__ = __rxor__ = symmetric_difference

    def xǁIndexedSetǁ__rsub____mutmut_orig(self, other):
        vals = [x for x in other if x not in self]
        return type(other)(vals)

    def xǁIndexedSetǁ__rsub____mutmut_1(self, other):
        vals = None
        return type(other)(vals)

    def xǁIndexedSetǁ__rsub____mutmut_2(self, other):
        vals = [x for x in other if x in self]
        return type(other)(vals)

    def xǁIndexedSetǁ__rsub____mutmut_3(self, other):
        vals = [x for x in other if x not in self]
        return type(other)(None)

    def xǁIndexedSetǁ__rsub____mutmut_4(self, other):
        vals = [x for x in other if x not in self]
        return type(None)(vals)
    
    xǁIndexedSetǁ__rsub____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__rsub____mutmut_1': xǁIndexedSetǁ__rsub____mutmut_1, 
        'xǁIndexedSetǁ__rsub____mutmut_2': xǁIndexedSetǁ__rsub____mutmut_2, 
        'xǁIndexedSetǁ__rsub____mutmut_3': xǁIndexedSetǁ__rsub____mutmut_3, 
        'xǁIndexedSetǁ__rsub____mutmut_4': xǁIndexedSetǁ__rsub____mutmut_4
    }
    
    def __rsub__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__rsub____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__rsub____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __rsub__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__rsub____mutmut_orig)
    xǁIndexedSetǁ__rsub____mutmut_orig.__name__ = 'xǁIndexedSetǁ__rsub__'

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_orig(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_1(self, *others):
        "XXupdate(*others) -> add values from one or more iterablesXX"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_2(self, *others):
        "UPDATE(*OTHERS) -> ADD VALUES FROM ONE OR MORE ITERABLES"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_3(self, *others):
        "update(*others) -> add values from one or more iterables"
        if others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_4(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) != 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_5(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 2:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_6(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = None
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_7(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[1]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_8(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = None
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_9(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(None)
        for o in other:
            self.add(o)

    # in-place set operations
    def xǁIndexedSetǁupdate__mutmut_10(self, *others):
        "update(*others) -> add values from one or more iterables"
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(None)
    
    xǁIndexedSetǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁupdate__mutmut_1': xǁIndexedSetǁupdate__mutmut_1, 
        'xǁIndexedSetǁupdate__mutmut_2': xǁIndexedSetǁupdate__mutmut_2, 
        'xǁIndexedSetǁupdate__mutmut_3': xǁIndexedSetǁupdate__mutmut_3, 
        'xǁIndexedSetǁupdate__mutmut_4': xǁIndexedSetǁupdate__mutmut_4, 
        'xǁIndexedSetǁupdate__mutmut_5': xǁIndexedSetǁupdate__mutmut_5, 
        'xǁIndexedSetǁupdate__mutmut_6': xǁIndexedSetǁupdate__mutmut_6, 
        'xǁIndexedSetǁupdate__mutmut_7': xǁIndexedSetǁupdate__mutmut_7, 
        'xǁIndexedSetǁupdate__mutmut_8': xǁIndexedSetǁupdate__mutmut_8, 
        'xǁIndexedSetǁupdate__mutmut_9': xǁIndexedSetǁupdate__mutmut_9, 
        'xǁIndexedSetǁupdate__mutmut_10': xǁIndexedSetǁupdate__mutmut_10
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁIndexedSetǁupdate__mutmut_orig)
    xǁIndexedSetǁupdate__mutmut_orig.__name__ = 'xǁIndexedSetǁupdate'

    def xǁIndexedSetǁintersection_update__mutmut_orig(self, *others):
        "intersection_update(*others) -> discard self.difference(*others)"
        for val in self.difference(*others):
            self.discard(val)

    def xǁIndexedSetǁintersection_update__mutmut_1(self, *others):
        "XXintersection_update(*others) -> discard self.difference(*others)XX"
        for val in self.difference(*others):
            self.discard(val)

    def xǁIndexedSetǁintersection_update__mutmut_2(self, *others):
        "INTERSECTION_UPDATE(*OTHERS) -> DISCARD SELF.DIFFERENCE(*OTHERS)"
        for val in self.difference(*others):
            self.discard(val)

    def xǁIndexedSetǁintersection_update__mutmut_3(self, *others):
        "intersection_update(*others) -> discard self.difference(*others)"
        for val in self.difference(*others):
            self.discard(None)
    
    xǁIndexedSetǁintersection_update__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁintersection_update__mutmut_1': xǁIndexedSetǁintersection_update__mutmut_1, 
        'xǁIndexedSetǁintersection_update__mutmut_2': xǁIndexedSetǁintersection_update__mutmut_2, 
        'xǁIndexedSetǁintersection_update__mutmut_3': xǁIndexedSetǁintersection_update__mutmut_3
    }
    
    def intersection_update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁintersection_update__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁintersection_update__mutmut_mutants"), args, kwargs, self)
        return result 
    
    intersection_update.__signature__ = _mutmut_signature(xǁIndexedSetǁintersection_update__mutmut_orig)
    xǁIndexedSetǁintersection_update__mutmut_orig.__name__ = 'xǁIndexedSetǁintersection_update'

    def xǁIndexedSetǁdifference_update__mutmut_orig(self, *others):
        "difference_update(*others) -> discard self.intersection(*others)"
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def xǁIndexedSetǁdifference_update__mutmut_1(self, *others):
        "XXdifference_update(*others) -> discard self.intersection(*others)XX"
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def xǁIndexedSetǁdifference_update__mutmut_2(self, *others):
        "DIFFERENCE_UPDATE(*OTHERS) -> DISCARD SELF.INTERSECTION(*OTHERS)"
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def xǁIndexedSetǁdifference_update__mutmut_3(self, *others):
        "difference_update(*others) -> discard self.intersection(*others)"
        if self not in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def xǁIndexedSetǁdifference_update__mutmut_4(self, *others):
        "difference_update(*others) -> discard self.intersection(*others)"
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(None)
    
    xǁIndexedSetǁdifference_update__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁdifference_update__mutmut_1': xǁIndexedSetǁdifference_update__mutmut_1, 
        'xǁIndexedSetǁdifference_update__mutmut_2': xǁIndexedSetǁdifference_update__mutmut_2, 
        'xǁIndexedSetǁdifference_update__mutmut_3': xǁIndexedSetǁdifference_update__mutmut_3, 
        'xǁIndexedSetǁdifference_update__mutmut_4': xǁIndexedSetǁdifference_update__mutmut_4
    }
    
    def difference_update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁdifference_update__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁdifference_update__mutmut_mutants"), args, kwargs, self)
        return result 
    
    difference_update.__signature__ = _mutmut_signature(xǁIndexedSetǁdifference_update__mutmut_orig)
    xǁIndexedSetǁdifference_update__mutmut_orig.__name__ = 'xǁIndexedSetǁdifference_update'

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_orig(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_1(self, other):  # note singular 'other'
        "XXsymmetric_difference_update(other) -> in-place XOR with otherXX"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_2(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place xor with other"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_3(self, other):  # note singular 'other'
        "SYMMETRIC_DIFFERENCE_UPDATE(OTHER) -> IN-PLACE XOR WITH OTHER"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_4(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is not other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_5(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is other:
            self.clear()
        for val in other:
            if val not in self:
                self.discard(val)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_6(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(None)
            else:
                self.add(val)

    def xǁIndexedSetǁsymmetric_difference_update__mutmut_7(self, other):  # note singular 'other'
        "symmetric_difference_update(other) -> in-place XOR with other"
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(None)
    
    xǁIndexedSetǁsymmetric_difference_update__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁsymmetric_difference_update__mutmut_1': xǁIndexedSetǁsymmetric_difference_update__mutmut_1, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_2': xǁIndexedSetǁsymmetric_difference_update__mutmut_2, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_3': xǁIndexedSetǁsymmetric_difference_update__mutmut_3, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_4': xǁIndexedSetǁsymmetric_difference_update__mutmut_4, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_5': xǁIndexedSetǁsymmetric_difference_update__mutmut_5, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_6': xǁIndexedSetǁsymmetric_difference_update__mutmut_6, 
        'xǁIndexedSetǁsymmetric_difference_update__mutmut_7': xǁIndexedSetǁsymmetric_difference_update__mutmut_7
    }
    
    def symmetric_difference_update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁsymmetric_difference_update__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁsymmetric_difference_update__mutmut_mutants"), args, kwargs, self)
        return result 
    
    symmetric_difference_update.__signature__ = _mutmut_signature(xǁIndexedSetǁsymmetric_difference_update__mutmut_orig)
    xǁIndexedSetǁsymmetric_difference_update__mutmut_orig.__name__ = 'xǁIndexedSetǁsymmetric_difference_update'

    def __ior__(self, *others):
        self.update(*others)
        return self

    def __iand__(self, *others):
        self.intersection_update(*others)
        return self

    def __isub__(self, *others):
        self.difference_update(*others)
        return self

    def __ixor__(self, *others):
        self.symmetric_difference_update(*others)
        return self

    def xǁIndexedSetǁiter_slice__mutmut_orig(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_1(self, start, stop, step=None):
        "XXiterate over a slice of the setXX"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_2(self, start, stop, step=None):
        "ITERATE OVER A SLICE OF THE SET"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_3(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = None
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_4(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_5(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = None
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_6(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(None)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_7(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_8(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = None
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_9(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(None)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_10(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None or step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_11(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_12(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step <= 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_13(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 1:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_14(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = None
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_15(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = +step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_16(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = None
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_17(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(None)
        return islice(iterable, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_18(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(None, start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_19(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, None, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_20(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, None, step)

    def xǁIndexedSetǁiter_slice__mutmut_21(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, None)

    def xǁIndexedSetǁiter_slice__mutmut_22(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(start, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_23(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, stop, step)

    def xǁIndexedSetǁiter_slice__mutmut_24(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, step)

    def xǁIndexedSetǁiter_slice__mutmut_25(self, start, stop, step=None):
        "iterate over a slice of the set"
        iterable = self
        if start is not None:
            start = self._get_real_index(start)
        if stop is not None:
            stop = self._get_real_index(stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, )
    
    xǁIndexedSetǁiter_slice__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁiter_slice__mutmut_1': xǁIndexedSetǁiter_slice__mutmut_1, 
        'xǁIndexedSetǁiter_slice__mutmut_2': xǁIndexedSetǁiter_slice__mutmut_2, 
        'xǁIndexedSetǁiter_slice__mutmut_3': xǁIndexedSetǁiter_slice__mutmut_3, 
        'xǁIndexedSetǁiter_slice__mutmut_4': xǁIndexedSetǁiter_slice__mutmut_4, 
        'xǁIndexedSetǁiter_slice__mutmut_5': xǁIndexedSetǁiter_slice__mutmut_5, 
        'xǁIndexedSetǁiter_slice__mutmut_6': xǁIndexedSetǁiter_slice__mutmut_6, 
        'xǁIndexedSetǁiter_slice__mutmut_7': xǁIndexedSetǁiter_slice__mutmut_7, 
        'xǁIndexedSetǁiter_slice__mutmut_8': xǁIndexedSetǁiter_slice__mutmut_8, 
        'xǁIndexedSetǁiter_slice__mutmut_9': xǁIndexedSetǁiter_slice__mutmut_9, 
        'xǁIndexedSetǁiter_slice__mutmut_10': xǁIndexedSetǁiter_slice__mutmut_10, 
        'xǁIndexedSetǁiter_slice__mutmut_11': xǁIndexedSetǁiter_slice__mutmut_11, 
        'xǁIndexedSetǁiter_slice__mutmut_12': xǁIndexedSetǁiter_slice__mutmut_12, 
        'xǁIndexedSetǁiter_slice__mutmut_13': xǁIndexedSetǁiter_slice__mutmut_13, 
        'xǁIndexedSetǁiter_slice__mutmut_14': xǁIndexedSetǁiter_slice__mutmut_14, 
        'xǁIndexedSetǁiter_slice__mutmut_15': xǁIndexedSetǁiter_slice__mutmut_15, 
        'xǁIndexedSetǁiter_slice__mutmut_16': xǁIndexedSetǁiter_slice__mutmut_16, 
        'xǁIndexedSetǁiter_slice__mutmut_17': xǁIndexedSetǁiter_slice__mutmut_17, 
        'xǁIndexedSetǁiter_slice__mutmut_18': xǁIndexedSetǁiter_slice__mutmut_18, 
        'xǁIndexedSetǁiter_slice__mutmut_19': xǁIndexedSetǁiter_slice__mutmut_19, 
        'xǁIndexedSetǁiter_slice__mutmut_20': xǁIndexedSetǁiter_slice__mutmut_20, 
        'xǁIndexedSetǁiter_slice__mutmut_21': xǁIndexedSetǁiter_slice__mutmut_21, 
        'xǁIndexedSetǁiter_slice__mutmut_22': xǁIndexedSetǁiter_slice__mutmut_22, 
        'xǁIndexedSetǁiter_slice__mutmut_23': xǁIndexedSetǁiter_slice__mutmut_23, 
        'xǁIndexedSetǁiter_slice__mutmut_24': xǁIndexedSetǁiter_slice__mutmut_24, 
        'xǁIndexedSetǁiter_slice__mutmut_25': xǁIndexedSetǁiter_slice__mutmut_25
    }
    
    def iter_slice(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁiter_slice__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁiter_slice__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iter_slice.__signature__ = _mutmut_signature(xǁIndexedSetǁiter_slice__mutmut_orig)
    xǁIndexedSetǁiter_slice__mutmut_orig.__name__ = 'xǁIndexedSetǁiter_slice'

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_orig(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_1(self, index):
        try:
            start, stop, step = None
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_2(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = None
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_3(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(None)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_4(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.rindex(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_5(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = None
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_6(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(None, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_7(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, None, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_8(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, None)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_9(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_10(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_11(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, )
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_12(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(None)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_13(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index <= 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_14(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 1:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_15(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index = len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_16(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index -= len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_17(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = None
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_18(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(None)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_19(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = None
        except IndexError:
            raise IndexError('IndexedSet index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_20(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError(None)
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_21(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('XXIndexedSet index out of rangeXX')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_22(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('indexedset index out of range')
        return ret

    # list operations
    def xǁIndexedSetǁ__getitem____mutmut_23(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        real_index = self._get_real_index(index)
        try:
            ret = self.item_list[real_index]
        except IndexError:
            raise IndexError('INDEXEDSET INDEX OUT OF RANGE')
        return ret
    
    xǁIndexedSetǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁ__getitem____mutmut_1': xǁIndexedSetǁ__getitem____mutmut_1, 
        'xǁIndexedSetǁ__getitem____mutmut_2': xǁIndexedSetǁ__getitem____mutmut_2, 
        'xǁIndexedSetǁ__getitem____mutmut_3': xǁIndexedSetǁ__getitem____mutmut_3, 
        'xǁIndexedSetǁ__getitem____mutmut_4': xǁIndexedSetǁ__getitem____mutmut_4, 
        'xǁIndexedSetǁ__getitem____mutmut_5': xǁIndexedSetǁ__getitem____mutmut_5, 
        'xǁIndexedSetǁ__getitem____mutmut_6': xǁIndexedSetǁ__getitem____mutmut_6, 
        'xǁIndexedSetǁ__getitem____mutmut_7': xǁIndexedSetǁ__getitem____mutmut_7, 
        'xǁIndexedSetǁ__getitem____mutmut_8': xǁIndexedSetǁ__getitem____mutmut_8, 
        'xǁIndexedSetǁ__getitem____mutmut_9': xǁIndexedSetǁ__getitem____mutmut_9, 
        'xǁIndexedSetǁ__getitem____mutmut_10': xǁIndexedSetǁ__getitem____mutmut_10, 
        'xǁIndexedSetǁ__getitem____mutmut_11': xǁIndexedSetǁ__getitem____mutmut_11, 
        'xǁIndexedSetǁ__getitem____mutmut_12': xǁIndexedSetǁ__getitem____mutmut_12, 
        'xǁIndexedSetǁ__getitem____mutmut_13': xǁIndexedSetǁ__getitem____mutmut_13, 
        'xǁIndexedSetǁ__getitem____mutmut_14': xǁIndexedSetǁ__getitem____mutmut_14, 
        'xǁIndexedSetǁ__getitem____mutmut_15': xǁIndexedSetǁ__getitem____mutmut_15, 
        'xǁIndexedSetǁ__getitem____mutmut_16': xǁIndexedSetǁ__getitem____mutmut_16, 
        'xǁIndexedSetǁ__getitem____mutmut_17': xǁIndexedSetǁ__getitem____mutmut_17, 
        'xǁIndexedSetǁ__getitem____mutmut_18': xǁIndexedSetǁ__getitem____mutmut_18, 
        'xǁIndexedSetǁ__getitem____mutmut_19': xǁIndexedSetǁ__getitem____mutmut_19, 
        'xǁIndexedSetǁ__getitem____mutmut_20': xǁIndexedSetǁ__getitem____mutmut_20, 
        'xǁIndexedSetǁ__getitem____mutmut_21': xǁIndexedSetǁ__getitem____mutmut_21, 
        'xǁIndexedSetǁ__getitem____mutmut_22': xǁIndexedSetǁ__getitem____mutmut_22, 
        'xǁIndexedSetǁ__getitem____mutmut_23': xǁIndexedSetǁ__getitem____mutmut_23
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁIndexedSetǁ__getitem____mutmut_orig)
    xǁIndexedSetǁ__getitem____mutmut_orig.__name__ = 'xǁIndexedSetǁ__getitem__'

    def xǁIndexedSetǁpop__mutmut_orig(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_1(self, index=None):
        "XXpop(index) -> remove the item at a given index (-1 by default)XX"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_2(self, index=None):
        "POP(INDEX) -> REMOVE THE ITEM AT A GIVEN INDEX (-1 BY DEFAULT)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_3(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = None
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_4(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = None
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_5(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 and index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_6(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None and index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_7(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is not None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_8(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index != -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_9(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == +1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_10(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -2 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_11(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index != len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_12(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self + 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_13(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 2:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_14(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = None
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_15(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = None
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_16(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(None)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_17(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = None
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_18(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = None
            del item_index_map[ret]
            self._add_dead(real_index)
        self._cull()
        return ret

    def xǁIndexedSetǁpop__mutmut_19(self, index=None):
        "pop(index) -> remove the item at a given index (-1 by default)"
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self - 1:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            real_index = self._get_real_index(index)
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
            self._add_dead(None)
        self._cull()
        return ret
    
    xǁIndexedSetǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁpop__mutmut_1': xǁIndexedSetǁpop__mutmut_1, 
        'xǁIndexedSetǁpop__mutmut_2': xǁIndexedSetǁpop__mutmut_2, 
        'xǁIndexedSetǁpop__mutmut_3': xǁIndexedSetǁpop__mutmut_3, 
        'xǁIndexedSetǁpop__mutmut_4': xǁIndexedSetǁpop__mutmut_4, 
        'xǁIndexedSetǁpop__mutmut_5': xǁIndexedSetǁpop__mutmut_5, 
        'xǁIndexedSetǁpop__mutmut_6': xǁIndexedSetǁpop__mutmut_6, 
        'xǁIndexedSetǁpop__mutmut_7': xǁIndexedSetǁpop__mutmut_7, 
        'xǁIndexedSetǁpop__mutmut_8': xǁIndexedSetǁpop__mutmut_8, 
        'xǁIndexedSetǁpop__mutmut_9': xǁIndexedSetǁpop__mutmut_9, 
        'xǁIndexedSetǁpop__mutmut_10': xǁIndexedSetǁpop__mutmut_10, 
        'xǁIndexedSetǁpop__mutmut_11': xǁIndexedSetǁpop__mutmut_11, 
        'xǁIndexedSetǁpop__mutmut_12': xǁIndexedSetǁpop__mutmut_12, 
        'xǁIndexedSetǁpop__mutmut_13': xǁIndexedSetǁpop__mutmut_13, 
        'xǁIndexedSetǁpop__mutmut_14': xǁIndexedSetǁpop__mutmut_14, 
        'xǁIndexedSetǁpop__mutmut_15': xǁIndexedSetǁpop__mutmut_15, 
        'xǁIndexedSetǁpop__mutmut_16': xǁIndexedSetǁpop__mutmut_16, 
        'xǁIndexedSetǁpop__mutmut_17': xǁIndexedSetǁpop__mutmut_17, 
        'xǁIndexedSetǁpop__mutmut_18': xǁIndexedSetǁpop__mutmut_18, 
        'xǁIndexedSetǁpop__mutmut_19': xǁIndexedSetǁpop__mutmut_19
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁpop__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁIndexedSetǁpop__mutmut_orig)
    xǁIndexedSetǁpop__mutmut_orig.__name__ = 'xǁIndexedSetǁpop'

    def xǁIndexedSetǁcount__mutmut_orig(self, val):
        "count(val) -> count number of instances of value (0 or 1)"
        if val in self.item_index_map:
            return 1
        return 0

    def xǁIndexedSetǁcount__mutmut_1(self, val):
        "XXcount(val) -> count number of instances of value (0 or 1)XX"
        if val in self.item_index_map:
            return 1
        return 0

    def xǁIndexedSetǁcount__mutmut_2(self, val):
        "COUNT(VAL) -> COUNT NUMBER OF INSTANCES OF VALUE (0 OR 1)"
        if val in self.item_index_map:
            return 1
        return 0

    def xǁIndexedSetǁcount__mutmut_3(self, val):
        "count(val) -> count number of instances of value (0 or 1)"
        if val not in self.item_index_map:
            return 1
        return 0

    def xǁIndexedSetǁcount__mutmut_4(self, val):
        "count(val) -> count number of instances of value (0 or 1)"
        if val in self.item_index_map:
            return 2
        return 0

    def xǁIndexedSetǁcount__mutmut_5(self, val):
        "count(val) -> count number of instances of value (0 or 1)"
        if val in self.item_index_map:
            return 1
        return 1
    
    xǁIndexedSetǁcount__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁcount__mutmut_1': xǁIndexedSetǁcount__mutmut_1, 
        'xǁIndexedSetǁcount__mutmut_2': xǁIndexedSetǁcount__mutmut_2, 
        'xǁIndexedSetǁcount__mutmut_3': xǁIndexedSetǁcount__mutmut_3, 
        'xǁIndexedSetǁcount__mutmut_4': xǁIndexedSetǁcount__mutmut_4, 
        'xǁIndexedSetǁcount__mutmut_5': xǁIndexedSetǁcount__mutmut_5
    }
    
    def count(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁcount__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁcount__mutmut_mutants"), args, kwargs, self)
        return result 
    
    count.__signature__ = _mutmut_signature(xǁIndexedSetǁcount__mutmut_orig)
    xǁIndexedSetǁcount__mutmut_orig.__name__ = 'xǁIndexedSetǁcount'

    def xǁIndexedSetǁreverse__mutmut_orig(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_1(self):
        "XXreverse() -> reverse the contents of the set in-placeXX"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_2(self):
        "REVERSE() -> REVERSE THE CONTENTS OF THE SET IN-PLACE"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_3(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = None
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_4(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(None)
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_5(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(None))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_6(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(self))
        self.item_list[:] = None
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_7(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(None):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁreverse__mutmut_8(self):
        "reverse() -> reverse the contents of the set in-place"
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = None
        del self.dead_indices[:]
    
    xǁIndexedSetǁreverse__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁreverse__mutmut_1': xǁIndexedSetǁreverse__mutmut_1, 
        'xǁIndexedSetǁreverse__mutmut_2': xǁIndexedSetǁreverse__mutmut_2, 
        'xǁIndexedSetǁreverse__mutmut_3': xǁIndexedSetǁreverse__mutmut_3, 
        'xǁIndexedSetǁreverse__mutmut_4': xǁIndexedSetǁreverse__mutmut_4, 
        'xǁIndexedSetǁreverse__mutmut_5': xǁIndexedSetǁreverse__mutmut_5, 
        'xǁIndexedSetǁreverse__mutmut_6': xǁIndexedSetǁreverse__mutmut_6, 
        'xǁIndexedSetǁreverse__mutmut_7': xǁIndexedSetǁreverse__mutmut_7, 
        'xǁIndexedSetǁreverse__mutmut_8': xǁIndexedSetǁreverse__mutmut_8
    }
    
    def reverse(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁreverse__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁreverse__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reverse.__signature__ = _mutmut_signature(xǁIndexedSetǁreverse__mutmut_orig)
    xǁIndexedSetǁreverse__mutmut_orig.__name__ = 'xǁIndexedSetǁreverse'

    def xǁIndexedSetǁsort__mutmut_orig(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_1(self, **kwargs):
        "XXsort() -> sort the contents of the set in-placeXX"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_2(self, **kwargs):
        "SORT() -> SORT THE CONTENTS OF THE SET IN-PLACE"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_3(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = None
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_4(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(None, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_5(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(**kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_6(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, )
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_7(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list != self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_8(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = None
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_9(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(None):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def xǁIndexedSetǁsort__mutmut_10(self, **kwargs):
        "sort() -> sort the contents of the set in-place"
        sorted_list = sorted(self, **kwargs)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = None
        del self.dead_indices[:]
    
    xǁIndexedSetǁsort__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁsort__mutmut_1': xǁIndexedSetǁsort__mutmut_1, 
        'xǁIndexedSetǁsort__mutmut_2': xǁIndexedSetǁsort__mutmut_2, 
        'xǁIndexedSetǁsort__mutmut_3': xǁIndexedSetǁsort__mutmut_3, 
        'xǁIndexedSetǁsort__mutmut_4': xǁIndexedSetǁsort__mutmut_4, 
        'xǁIndexedSetǁsort__mutmut_5': xǁIndexedSetǁsort__mutmut_5, 
        'xǁIndexedSetǁsort__mutmut_6': xǁIndexedSetǁsort__mutmut_6, 
        'xǁIndexedSetǁsort__mutmut_7': xǁIndexedSetǁsort__mutmut_7, 
        'xǁIndexedSetǁsort__mutmut_8': xǁIndexedSetǁsort__mutmut_8, 
        'xǁIndexedSetǁsort__mutmut_9': xǁIndexedSetǁsort__mutmut_9, 
        'xǁIndexedSetǁsort__mutmut_10': xǁIndexedSetǁsort__mutmut_10
    }
    
    def sort(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁsort__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁsort__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sort.__signature__ = _mutmut_signature(xǁIndexedSetǁsort__mutmut_orig)
    xǁIndexedSetǁsort__mutmut_orig.__name__ = 'xǁIndexedSetǁsort'

    def xǁIndexedSetǁindex__mutmut_orig(self, val):
        "index(val) -> get the index of a value, raises if not present"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(f'{val!r} is not in {cn}')

    def xǁIndexedSetǁindex__mutmut_1(self, val):
        "XXindex(val) -> get the index of a value, raises if not presentXX"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(f'{val!r} is not in {cn}')

    def xǁIndexedSetǁindex__mutmut_2(self, val):
        "INDEX(VAL) -> GET THE INDEX OF A VALUE, RAISES IF NOT PRESENT"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(f'{val!r} is not in {cn}')

    def xǁIndexedSetǁindex__mutmut_3(self, val):
        "index(val) -> get the index of a value, raises if not present"
        try:
            return self._get_apparent_index(None)
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(f'{val!r} is not in {cn}')

    def xǁIndexedSetǁindex__mutmut_4(self, val):
        "index(val) -> get the index of a value, raises if not present"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = None
            raise ValueError(f'{val!r} is not in {cn}')

    def xǁIndexedSetǁindex__mutmut_5(self, val):
        "index(val) -> get the index of a value, raises if not present"
        try:
            return self._get_apparent_index(self.item_index_map[val])
        except KeyError:
            cn = self.__class__.__name__
            raise ValueError(None)
    
    xǁIndexedSetǁindex__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIndexedSetǁindex__mutmut_1': xǁIndexedSetǁindex__mutmut_1, 
        'xǁIndexedSetǁindex__mutmut_2': xǁIndexedSetǁindex__mutmut_2, 
        'xǁIndexedSetǁindex__mutmut_3': xǁIndexedSetǁindex__mutmut_3, 
        'xǁIndexedSetǁindex__mutmut_4': xǁIndexedSetǁindex__mutmut_4, 
        'xǁIndexedSetǁindex__mutmut_5': xǁIndexedSetǁindex__mutmut_5
    }
    
    def index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIndexedSetǁindex__mutmut_orig"), object.__getattribute__(self, "xǁIndexedSetǁindex__mutmut_mutants"), args, kwargs, self)
        return result 
    
    index.__signature__ = _mutmut_signature(xǁIndexedSetǁindex__mutmut_orig)
    xǁIndexedSetǁindex__mutmut_orig.__name__ = 'xǁIndexedSetǁindex'


def x_complement__mutmut_orig(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_1(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(None) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_2(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is not _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_3(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(None) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_4(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is not frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_5(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=None)
    return _ComplementSet(excluded=set(wrapped))


def x_complement__mutmut_6(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=None)


def x_complement__mutmut_7(wrapped):
    """Given a :class:`set`, convert it to a **complement set**.

    Whereas a :class:`set` keeps track of what it contains, a
    `complement set
    <https://en.wikipedia.org/wiki/Complement_(set_theory)>`_ keeps
    track of what it does *not* contain. For example, look what
    happens when we intersect a normal set with a complement set::

    >>> list(set(range(5)) & complement(set([2, 3])))
    [0, 1, 4]

    We get the everything in the left that wasn't in the right,
    because intersecting with a complement is the same as subtracting
    a normal set.

    Args:
        wrapped (set): A set or any other iterable which should be
           turned into a complement set.

    All set methods and operators are supported by complement sets,
    between other :func:`complement`-wrapped sets and/or regular
    :class:`set` objects.

    Because a complement set only tracks what elements are *not* in
    the set, functionality based on set contents is unavailable:
    :func:`len`, :func:`iter` (and for loops), and ``.pop()``. But a
    complement set can always be turned back into a regular set by
    complementing it again:

    >>> s = set(range(5))
    >>> complement(complement(s)) == s
    True

    .. note::

       An empty complement set corresponds to the concept of a
       `universal set <https://en.wikipedia.org/wiki/Universal_set>`_
       from mathematics.

    Complement sets by example
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Many uses of sets can be expressed more simply by using a
    complement. Rather than trying to work out in your head the proper
    way to invert an expression, you can just throw a complement on
    the set. Consider this example of a name filter::

        >>> class NamesFilter(object):
        ...    def __init__(self, allowed):
        ...        self._allowed = allowed
        ...
        ...    def filter(self, names):
        ...        return [name for name in names if name in self._allowed]
        >>> NamesFilter(set(['alice', 'bob'])).filter(['alice', 'bob', 'carol'])
        ['alice', 'bob']

    What if we want to just express "let all the names through"?

    We could try to enumerate all of the expected names::

       ``NamesFilter({'alice', 'bob', 'carol'})``

    But this is very brittle -- what if at some point over this
    object is changed to filter ``['alice', 'bob', 'carol', 'dan']``?

    Even worse, what about the poor programmer who next works
    on this piece of code?  They cannot tell whether the purpose
    of the large allowed set was "allow everything", or if 'dan'
    was excluded for some subtle reason.

    A complement set lets the programmer intention be expressed
    succinctly and directly::

       NamesFilter(complement(set()))

    Not only is this code short and robust, it is easy to understand
    the intention.

    """
    if type(wrapped) is _ComplementSet:
        return wrapped.complemented()
    if type(wrapped) is frozenset:
        return _ComplementSet(excluded=wrapped)
    return _ComplementSet(excluded=set(None))

x_complement__mutmut_mutants : ClassVar[MutantDict] = {
'x_complement__mutmut_1': x_complement__mutmut_1, 
    'x_complement__mutmut_2': x_complement__mutmut_2, 
    'x_complement__mutmut_3': x_complement__mutmut_3, 
    'x_complement__mutmut_4': x_complement__mutmut_4, 
    'x_complement__mutmut_5': x_complement__mutmut_5, 
    'x_complement__mutmut_6': x_complement__mutmut_6, 
    'x_complement__mutmut_7': x_complement__mutmut_7
}

def complement(*args, **kwargs):
    result = _mutmut_trampoline(x_complement__mutmut_orig, x_complement__mutmut_mutants, args, kwargs)
    return result 

complement.__signature__ = _mutmut_signature(x_complement__mutmut_orig)
x_complement__mutmut_orig.__name__ = 'x_complement'


def x__norm_args_typeerror__mutmut_orig(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_1(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(None) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_2(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) not in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_3(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_4(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(None) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_5(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is not _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_6(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = None
    else:
        raise TypeError('argument must be another set or complement(set)')
    return inc, exc


def x__norm_args_typeerror__mutmut_7(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError(None)
    return inc, exc


def x__norm_args_typeerror__mutmut_8(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('XXargument must be another set or complement(set)XX')
    return inc, exc


def x__norm_args_typeerror__mutmut_9(other):
    '''normalize args and raise type-error if there is a problem'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    return inc, exc

x__norm_args_typeerror__mutmut_mutants : ClassVar[MutantDict] = {
'x__norm_args_typeerror__mutmut_1': x__norm_args_typeerror__mutmut_1, 
    'x__norm_args_typeerror__mutmut_2': x__norm_args_typeerror__mutmut_2, 
    'x__norm_args_typeerror__mutmut_3': x__norm_args_typeerror__mutmut_3, 
    'x__norm_args_typeerror__mutmut_4': x__norm_args_typeerror__mutmut_4, 
    'x__norm_args_typeerror__mutmut_5': x__norm_args_typeerror__mutmut_5, 
    'x__norm_args_typeerror__mutmut_6': x__norm_args_typeerror__mutmut_6, 
    'x__norm_args_typeerror__mutmut_7': x__norm_args_typeerror__mutmut_7, 
    'x__norm_args_typeerror__mutmut_8': x__norm_args_typeerror__mutmut_8, 
    'x__norm_args_typeerror__mutmut_9': x__norm_args_typeerror__mutmut_9
}

def _norm_args_typeerror(*args, **kwargs):
    result = _mutmut_trampoline(x__norm_args_typeerror__mutmut_orig, x__norm_args_typeerror__mutmut_mutants, args, kwargs)
    return result 

_norm_args_typeerror.__signature__ = _mutmut_signature(x__norm_args_typeerror__mutmut_orig)
x__norm_args_typeerror__mutmut_orig.__name__ = 'x__norm_args_typeerror'


def x__norm_args_notimplemented__mutmut_orig(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_1(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(None) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_2(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) not in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_3(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = None
    elif type(other) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_4(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(None) is _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_5(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is not _ComplementSet:
        inc, exc = other._included, other._excluded
    else:
        return NotImplemented, None
    return inc, exc


def x__norm_args_notimplemented__mutmut_6(other):
    '''normalize args and return NotImplemented (for overloaded operators)'''
    if type(other) in (set, frozenset):
        inc, exc = other, None
    elif type(other) is _ComplementSet:
        inc, exc = None
    else:
        return NotImplemented, None
    return inc, exc

x__norm_args_notimplemented__mutmut_mutants : ClassVar[MutantDict] = {
'x__norm_args_notimplemented__mutmut_1': x__norm_args_notimplemented__mutmut_1, 
    'x__norm_args_notimplemented__mutmut_2': x__norm_args_notimplemented__mutmut_2, 
    'x__norm_args_notimplemented__mutmut_3': x__norm_args_notimplemented__mutmut_3, 
    'x__norm_args_notimplemented__mutmut_4': x__norm_args_notimplemented__mutmut_4, 
    'x__norm_args_notimplemented__mutmut_5': x__norm_args_notimplemented__mutmut_5, 
    'x__norm_args_notimplemented__mutmut_6': x__norm_args_notimplemented__mutmut_6
}

def _norm_args_notimplemented(*args, **kwargs):
    result = _mutmut_trampoline(x__norm_args_notimplemented__mutmut_orig, x__norm_args_notimplemented__mutmut_mutants, args, kwargs)
    return result 

_norm_args_notimplemented.__signature__ = _mutmut_signature(x__norm_args_notimplemented__mutmut_orig)
x__norm_args_notimplemented__mutmut_orig.__name__ = 'x__norm_args_notimplemented'


class _ComplementSet:
    """
    helper class for complement() that implements the set methods
    """
    __slots__ = ('_included', '_excluded')

    def xǁ_ComplementSetǁ__init____mutmut_orig(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_1(self, included=None, excluded=None):
        if included is not None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_2(self, included=None, excluded=None):
        if included is None:
            assert type(None) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_3(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) not in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_4(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is not None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_5(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(None) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_6(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) not in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_7(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError(None)
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_8(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('XXone of included or excluded must be a setXX')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_9(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('ONE OF INCLUDED OR EXCLUDED MUST BE A SET')
        self._included, self._excluded = included, excluded

    def xǁ_ComplementSetǁ__init____mutmut_10(self, included=None, excluded=None):
        if included is None:
            assert type(excluded) in (set, frozenset)
        elif excluded is None:
            assert type(included) in (set, frozenset)
        else:
            raise ValueError('one of included or excluded must be a set')
        self._included, self._excluded = None
    
    xǁ_ComplementSetǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__init____mutmut_1': xǁ_ComplementSetǁ__init____mutmut_1, 
        'xǁ_ComplementSetǁ__init____mutmut_2': xǁ_ComplementSetǁ__init____mutmut_2, 
        'xǁ_ComplementSetǁ__init____mutmut_3': xǁ_ComplementSetǁ__init____mutmut_3, 
        'xǁ_ComplementSetǁ__init____mutmut_4': xǁ_ComplementSetǁ__init____mutmut_4, 
        'xǁ_ComplementSetǁ__init____mutmut_5': xǁ_ComplementSetǁ__init____mutmut_5, 
        'xǁ_ComplementSetǁ__init____mutmut_6': xǁ_ComplementSetǁ__init____mutmut_6, 
        'xǁ_ComplementSetǁ__init____mutmut_7': xǁ_ComplementSetǁ__init____mutmut_7, 
        'xǁ_ComplementSetǁ__init____mutmut_8': xǁ_ComplementSetǁ__init____mutmut_8, 
        'xǁ_ComplementSetǁ__init____mutmut_9': xǁ_ComplementSetǁ__init____mutmut_9, 
        'xǁ_ComplementSetǁ__init____mutmut_10': xǁ_ComplementSetǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__init____mutmut_orig)
    xǁ_ComplementSetǁ__init____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__init__'

    def xǁ_ComplementSetǁ__repr____mutmut_orig(self):
        if self._included is None:
            return f'complement({repr(self._excluded)})'
        return f'complement(complement({repr(self._included)}))'

    def xǁ_ComplementSetǁ__repr____mutmut_1(self):
        if self._included is not None:
            return f'complement({repr(self._excluded)})'
        return f'complement(complement({repr(self._included)}))'

    def xǁ_ComplementSetǁ__repr____mutmut_2(self):
        if self._included is None:
            return f'complement({repr(None)})'
        return f'complement(complement({repr(self._included)}))'

    def xǁ_ComplementSetǁ__repr____mutmut_3(self):
        if self._included is None:
            return f'complement({repr(self._excluded)})'
        return f'complement(complement({repr(None)}))'
    
    xǁ_ComplementSetǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__repr____mutmut_1': xǁ_ComplementSetǁ__repr____mutmut_1, 
        'xǁ_ComplementSetǁ__repr____mutmut_2': xǁ_ComplementSetǁ__repr____mutmut_2, 
        'xǁ_ComplementSetǁ__repr____mutmut_3': xǁ_ComplementSetǁ__repr____mutmut_3
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__repr____mutmut_orig)
    xǁ_ComplementSetǁ__repr____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__repr__'

    def xǁ_ComplementSetǁcomplemented__mutmut_orig(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_1(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset and type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_2(self):
        '''return a complement of the current set'''
        if type(None) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_3(self):
        '''return a complement of the current set'''
        if type(self._included) is not frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_4(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(None) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_5(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is not frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_6(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=None, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_7(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=None)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_8(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_9(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, )
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_10(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None,
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_11(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None)

    def xǁ_ComplementSetǁcomplemented__mutmut_12(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_13(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            )

    def xǁ_ComplementSetǁcomplemented__mutmut_14(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is not None else set(self._excluded),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_15(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(None),
            excluded=None if self._included is None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_16(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is not None else set(self._included))

    def xǁ_ComplementSetǁcomplemented__mutmut_17(self):
        '''return a complement of the current set'''
        if type(self._included) is frozenset or type(self._excluded) is frozenset:
            return _ComplementSet(included=self._excluded, excluded=self._included)
        return _ComplementSet(
            included=None if self._excluded is None else set(self._excluded),
            excluded=None if self._included is None else set(None))
    
    xǁ_ComplementSetǁcomplemented__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁcomplemented__mutmut_1': xǁ_ComplementSetǁcomplemented__mutmut_1, 
        'xǁ_ComplementSetǁcomplemented__mutmut_2': xǁ_ComplementSetǁcomplemented__mutmut_2, 
        'xǁ_ComplementSetǁcomplemented__mutmut_3': xǁ_ComplementSetǁcomplemented__mutmut_3, 
        'xǁ_ComplementSetǁcomplemented__mutmut_4': xǁ_ComplementSetǁcomplemented__mutmut_4, 
        'xǁ_ComplementSetǁcomplemented__mutmut_5': xǁ_ComplementSetǁcomplemented__mutmut_5, 
        'xǁ_ComplementSetǁcomplemented__mutmut_6': xǁ_ComplementSetǁcomplemented__mutmut_6, 
        'xǁ_ComplementSetǁcomplemented__mutmut_7': xǁ_ComplementSetǁcomplemented__mutmut_7, 
        'xǁ_ComplementSetǁcomplemented__mutmut_8': xǁ_ComplementSetǁcomplemented__mutmut_8, 
        'xǁ_ComplementSetǁcomplemented__mutmut_9': xǁ_ComplementSetǁcomplemented__mutmut_9, 
        'xǁ_ComplementSetǁcomplemented__mutmut_10': xǁ_ComplementSetǁcomplemented__mutmut_10, 
        'xǁ_ComplementSetǁcomplemented__mutmut_11': xǁ_ComplementSetǁcomplemented__mutmut_11, 
        'xǁ_ComplementSetǁcomplemented__mutmut_12': xǁ_ComplementSetǁcomplemented__mutmut_12, 
        'xǁ_ComplementSetǁcomplemented__mutmut_13': xǁ_ComplementSetǁcomplemented__mutmut_13, 
        'xǁ_ComplementSetǁcomplemented__mutmut_14': xǁ_ComplementSetǁcomplemented__mutmut_14, 
        'xǁ_ComplementSetǁcomplemented__mutmut_15': xǁ_ComplementSetǁcomplemented__mutmut_15, 
        'xǁ_ComplementSetǁcomplemented__mutmut_16': xǁ_ComplementSetǁcomplemented__mutmut_16, 
        'xǁ_ComplementSetǁcomplemented__mutmut_17': xǁ_ComplementSetǁcomplemented__mutmut_17
    }
    
    def complemented(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁcomplemented__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁcomplemented__mutmut_mutants"), args, kwargs, self)
        return result 
    
    complemented.__signature__ = _mutmut_signature(xǁ_ComplementSetǁcomplemented__mutmut_orig)
    xǁ_ComplementSetǁcomplemented__mutmut_orig.__name__ = 'xǁ_ComplementSetǁcomplemented'

    __invert__ = complemented

    def xǁ_ComplementSetǁcomplement__mutmut_orig(self):
        '''convert the current set to its complement in-place'''
        self._included, self._excluded = self._excluded, self._included

    def xǁ_ComplementSetǁcomplement__mutmut_1(self):
        '''convert the current set to its complement in-place'''
        self._included, self._excluded = None
    
    xǁ_ComplementSetǁcomplement__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁcomplement__mutmut_1': xǁ_ComplementSetǁcomplement__mutmut_1
    }
    
    def complement(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁcomplement__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁcomplement__mutmut_mutants"), args, kwargs, self)
        return result 
    
    complement.__signature__ = _mutmut_signature(xǁ_ComplementSetǁcomplement__mutmut_orig)
    xǁ_ComplementSetǁcomplement__mutmut_orig.__name__ = 'xǁ_ComplementSetǁcomplement'

    def xǁ_ComplementSetǁ__contains____mutmut_orig(self, item):
        if self._included is None:
            return not item in self._excluded
        return item in self._included

    def xǁ_ComplementSetǁ__contains____mutmut_1(self, item):
        if self._included is not None:
            return not item in self._excluded
        return item in self._included

    def xǁ_ComplementSetǁ__contains____mutmut_2(self, item):
        if self._included is None:
            return item in self._excluded
        return item in self._included

    def xǁ_ComplementSetǁ__contains____mutmut_3(self, item):
        if self._included is None:
            return not item not in self._excluded
        return item in self._included

    def xǁ_ComplementSetǁ__contains____mutmut_4(self, item):
        if self._included is None:
            return not item in self._excluded
        return item not in self._included
    
    xǁ_ComplementSetǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__contains____mutmut_1': xǁ_ComplementSetǁ__contains____mutmut_1, 
        'xǁ_ComplementSetǁ__contains____mutmut_2': xǁ_ComplementSetǁ__contains____mutmut_2, 
        'xǁ_ComplementSetǁ__contains____mutmut_3': xǁ_ComplementSetǁ__contains____mutmut_3, 
        'xǁ_ComplementSetǁ__contains____mutmut_4': xǁ_ComplementSetǁ__contains____mutmut_4
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__contains____mutmut_orig)
    xǁ_ComplementSetǁ__contains____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__contains__'

    def xǁ_ComplementSetǁadd__mutmut_orig(self, item):
        if self._included is None:
            if item in self._excluded:
                self._excluded.remove(item)
        else:
            self._included.add(item)

    def xǁ_ComplementSetǁadd__mutmut_1(self, item):
        if self._included is not None:
            if item in self._excluded:
                self._excluded.remove(item)
        else:
            self._included.add(item)

    def xǁ_ComplementSetǁadd__mutmut_2(self, item):
        if self._included is None:
            if item not in self._excluded:
                self._excluded.remove(item)
        else:
            self._included.add(item)

    def xǁ_ComplementSetǁadd__mutmut_3(self, item):
        if self._included is None:
            if item in self._excluded:
                self._excluded.remove(None)
        else:
            self._included.add(item)

    def xǁ_ComplementSetǁadd__mutmut_4(self, item):
        if self._included is None:
            if item in self._excluded:
                self._excluded.remove(item)
        else:
            self._included.add(None)
    
    xǁ_ComplementSetǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁadd__mutmut_1': xǁ_ComplementSetǁadd__mutmut_1, 
        'xǁ_ComplementSetǁadd__mutmut_2': xǁ_ComplementSetǁadd__mutmut_2, 
        'xǁ_ComplementSetǁadd__mutmut_3': xǁ_ComplementSetǁadd__mutmut_3, 
        'xǁ_ComplementSetǁadd__mutmut_4': xǁ_ComplementSetǁadd__mutmut_4
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁadd__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁ_ComplementSetǁadd__mutmut_orig)
    xǁ_ComplementSetǁadd__mutmut_orig.__name__ = 'xǁ_ComplementSetǁadd'

    def xǁ_ComplementSetǁremove__mutmut_orig(self, item):
        if self._included is None:
            self._excluded.add(item)
        else:
            self._included.remove(item)

    def xǁ_ComplementSetǁremove__mutmut_1(self, item):
        if self._included is not None:
            self._excluded.add(item)
        else:
            self._included.remove(item)

    def xǁ_ComplementSetǁremove__mutmut_2(self, item):
        if self._included is None:
            self._excluded.add(None)
        else:
            self._included.remove(item)

    def xǁ_ComplementSetǁremove__mutmut_3(self, item):
        if self._included is None:
            self._excluded.add(item)
        else:
            self._included.remove(None)
    
    xǁ_ComplementSetǁremove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁremove__mutmut_1': xǁ_ComplementSetǁremove__mutmut_1, 
        'xǁ_ComplementSetǁremove__mutmut_2': xǁ_ComplementSetǁremove__mutmut_2, 
        'xǁ_ComplementSetǁremove__mutmut_3': xǁ_ComplementSetǁremove__mutmut_3
    }
    
    def remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁremove__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁremove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    remove.__signature__ = _mutmut_signature(xǁ_ComplementSetǁremove__mutmut_orig)
    xǁ_ComplementSetǁremove__mutmut_orig.__name__ = 'xǁ_ComplementSetǁremove'

    def xǁ_ComplementSetǁpop__mutmut_orig(self):
        if self._included is None:
            raise NotImplementedError  # self.missing.add(random.choice(gc.objects()))
        return self._included.pop()

    def xǁ_ComplementSetǁpop__mutmut_1(self):
        if self._included is not None:
            raise NotImplementedError  # self.missing.add(random.choice(gc.objects()))
        return self._included.pop()
    
    xǁ_ComplementSetǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁpop__mutmut_1': xǁ_ComplementSetǁpop__mutmut_1
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁpop__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁ_ComplementSetǁpop__mutmut_orig)
    xǁ_ComplementSetǁpop__mutmut_orig.__name__ = 'xǁ_ComplementSetǁpop'

    def xǁ_ComplementSetǁintersection__mutmut_orig(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁintersection__mutmut_1(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁintersection__mutmut_2(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁintersection__mutmut_3(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁintersection__mutmut_4(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁintersection__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁintersection__mutmut_1': xǁ_ComplementSetǁintersection__mutmut_1, 
        'xǁ_ComplementSetǁintersection__mutmut_2': xǁ_ComplementSetǁintersection__mutmut_2, 
        'xǁ_ComplementSetǁintersection__mutmut_3': xǁ_ComplementSetǁintersection__mutmut_3, 
        'xǁ_ComplementSetǁintersection__mutmut_4': xǁ_ComplementSetǁintersection__mutmut_4
    }
    
    def intersection(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁintersection__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁintersection__mutmut_mutants"), args, kwargs, self)
        return result 
    
    intersection.__signature__ = _mutmut_signature(xǁ_ComplementSetǁintersection__mutmut_orig)
    xǁ_ComplementSetǁintersection__mutmut_orig.__name__ = 'xǁ_ComplementSetǁintersection'

    def xǁ_ComplementSetǁ__and____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=None)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc + self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=None)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(None))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is not None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=None)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc + self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(inc))

    def xǁ_ComplementSetǁ__and____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=None)

    def xǁ_ComplementSetǁ__and____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc - self._excluded)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.union(other._excluded))
        else:
            if inc is None:  # + -
                return _ComplementSet(included=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.intersection(None))
    
    xǁ_ComplementSetǁ__and____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__and____mutmut_1': xǁ_ComplementSetǁ__and____mutmut_1, 
        'xǁ_ComplementSetǁ__and____mutmut_2': xǁ_ComplementSetǁ__and____mutmut_2, 
        'xǁ_ComplementSetǁ__and____mutmut_3': xǁ_ComplementSetǁ__and____mutmut_3, 
        'xǁ_ComplementSetǁ__and____mutmut_4': xǁ_ComplementSetǁ__and____mutmut_4, 
        'xǁ_ComplementSetǁ__and____mutmut_5': xǁ_ComplementSetǁ__and____mutmut_5, 
        'xǁ_ComplementSetǁ__and____mutmut_6': xǁ_ComplementSetǁ__and____mutmut_6, 
        'xǁ_ComplementSetǁ__and____mutmut_7': xǁ_ComplementSetǁ__and____mutmut_7, 
        'xǁ_ComplementSetǁ__and____mutmut_8': xǁ_ComplementSetǁ__and____mutmut_8, 
        'xǁ_ComplementSetǁ__and____mutmut_9': xǁ_ComplementSetǁ__and____mutmut_9, 
        'xǁ_ComplementSetǁ__and____mutmut_10': xǁ_ComplementSetǁ__and____mutmut_10, 
        'xǁ_ComplementSetǁ__and____mutmut_11': xǁ_ComplementSetǁ__and____mutmut_11, 
        'xǁ_ComplementSetǁ__and____mutmut_12': xǁ_ComplementSetǁ__and____mutmut_12, 
        'xǁ_ComplementSetǁ__and____mutmut_13': xǁ_ComplementSetǁ__and____mutmut_13, 
        'xǁ_ComplementSetǁ__and____mutmut_14': xǁ_ComplementSetǁ__and____mutmut_14
    }
    
    def __and__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__and____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__and____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __and__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__and____mutmut_orig)
    xǁ_ComplementSetǁ__and____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__and__'

    __rand__ = __and__

    def xǁ_ComplementSetǁ__iand____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = None  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc + self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded = exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is not None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included = exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included += exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None
            else:  # + +
                self._included &= inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included = inc
        return self

    def xǁ_ComplementSetǁ__iand____mutmut_15(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc - self._excluded  # TODO: do this in place?
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included -= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included |= inc
        return self
    
    xǁ_ComplementSetǁ__iand____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__iand____mutmut_1': xǁ_ComplementSetǁ__iand____mutmut_1, 
        'xǁ_ComplementSetǁ__iand____mutmut_2': xǁ_ComplementSetǁ__iand____mutmut_2, 
        'xǁ_ComplementSetǁ__iand____mutmut_3': xǁ_ComplementSetǁ__iand____mutmut_3, 
        'xǁ_ComplementSetǁ__iand____mutmut_4': xǁ_ComplementSetǁ__iand____mutmut_4, 
        'xǁ_ComplementSetǁ__iand____mutmut_5': xǁ_ComplementSetǁ__iand____mutmut_5, 
        'xǁ_ComplementSetǁ__iand____mutmut_6': xǁ_ComplementSetǁ__iand____mutmut_6, 
        'xǁ_ComplementSetǁ__iand____mutmut_7': xǁ_ComplementSetǁ__iand____mutmut_7, 
        'xǁ_ComplementSetǁ__iand____mutmut_8': xǁ_ComplementSetǁ__iand____mutmut_8, 
        'xǁ_ComplementSetǁ__iand____mutmut_9': xǁ_ComplementSetǁ__iand____mutmut_9, 
        'xǁ_ComplementSetǁ__iand____mutmut_10': xǁ_ComplementSetǁ__iand____mutmut_10, 
        'xǁ_ComplementSetǁ__iand____mutmut_11': xǁ_ComplementSetǁ__iand____mutmut_11, 
        'xǁ_ComplementSetǁ__iand____mutmut_12': xǁ_ComplementSetǁ__iand____mutmut_12, 
        'xǁ_ComplementSetǁ__iand____mutmut_13': xǁ_ComplementSetǁ__iand____mutmut_13, 
        'xǁ_ComplementSetǁ__iand____mutmut_14': xǁ_ComplementSetǁ__iand____mutmut_14, 
        'xǁ_ComplementSetǁ__iand____mutmut_15': xǁ_ComplementSetǁ__iand____mutmut_15
    }
    
    def __iand__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__iand____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__iand____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iand__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__iand____mutmut_orig)
    xǁ_ComplementSetǁ__iand____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__iand__'

    def xǁ_ComplementSetǁunion__mutmut_orig(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁunion__mutmut_1(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁunion__mutmut_2(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁunion__mutmut_3(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁunion__mutmut_4(self, other):
        try:
            return self | other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁunion__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁunion__mutmut_1': xǁ_ComplementSetǁunion__mutmut_1, 
        'xǁ_ComplementSetǁunion__mutmut_2': xǁ_ComplementSetǁunion__mutmut_2, 
        'xǁ_ComplementSetǁunion__mutmut_3': xǁ_ComplementSetǁunion__mutmut_3, 
        'xǁ_ComplementSetǁunion__mutmut_4': xǁ_ComplementSetǁunion__mutmut_4
    }
    
    def union(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁunion__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁunion__mutmut_mutants"), args, kwargs, self)
        return result 
    
    union.__signature__ = _mutmut_signature(xǁ_ComplementSetǁunion__mutmut_orig)
    xǁ_ComplementSetǁunion__mutmut_orig.__name__ = 'xǁ_ComplementSetǁunion'

    def xǁ_ComplementSetǁ__or____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=None)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded + inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=None)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(None))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is not None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=None)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc + self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(inc))

    def xǁ_ComplementSetǁ__or____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=None)

    def xǁ_ComplementSetǁ__or____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(excluded=self._excluded.intersection(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.union(None))
    
    xǁ_ComplementSetǁ__or____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__or____mutmut_1': xǁ_ComplementSetǁ__or____mutmut_1, 
        'xǁ_ComplementSetǁ__or____mutmut_2': xǁ_ComplementSetǁ__or____mutmut_2, 
        'xǁ_ComplementSetǁ__or____mutmut_3': xǁ_ComplementSetǁ__or____mutmut_3, 
        'xǁ_ComplementSetǁ__or____mutmut_4': xǁ_ComplementSetǁ__or____mutmut_4, 
        'xǁ_ComplementSetǁ__or____mutmut_5': xǁ_ComplementSetǁ__or____mutmut_5, 
        'xǁ_ComplementSetǁ__or____mutmut_6': xǁ_ComplementSetǁ__or____mutmut_6, 
        'xǁ_ComplementSetǁ__or____mutmut_7': xǁ_ComplementSetǁ__or____mutmut_7, 
        'xǁ_ComplementSetǁ__or____mutmut_8': xǁ_ComplementSetǁ__or____mutmut_8, 
        'xǁ_ComplementSetǁ__or____mutmut_9': xǁ_ComplementSetǁ__or____mutmut_9, 
        'xǁ_ComplementSetǁ__or____mutmut_10': xǁ_ComplementSetǁ__or____mutmut_10, 
        'xǁ_ComplementSetǁ__or____mutmut_11': xǁ_ComplementSetǁ__or____mutmut_11, 
        'xǁ_ComplementSetǁ__or____mutmut_12': xǁ_ComplementSetǁ__or____mutmut_12, 
        'xǁ_ComplementSetǁ__or____mutmut_13': xǁ_ComplementSetǁ__or____mutmut_13, 
        'xǁ_ComplementSetǁ__or____mutmut_14': xǁ_ComplementSetǁ__or____mutmut_14
    }
    
    def __or__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__or____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__or____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __or__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__or____mutmut_orig)
    xǁ_ComplementSetǁ__or____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__or__'

    __ror__ = __or__

    def xǁ_ComplementSetǁ__ior____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded += inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded = exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded |= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is not None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc + self._included   # TODO: do this in place?
            else:  # + +
                self._included |= inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included = inc
        return self

    def xǁ_ComplementSetǁ__ior____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded -= inc
            else:  # - -
                self._excluded &= exc
        else:
            if inc is None:  # + -
                self._included, self._excluded = None, exc - self._included   # TODO: do this in place?
            else:  # + +
                self._included &= inc
        return self
    
    xǁ_ComplementSetǁ__ior____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__ior____mutmut_1': xǁ_ComplementSetǁ__ior____mutmut_1, 
        'xǁ_ComplementSetǁ__ior____mutmut_2': xǁ_ComplementSetǁ__ior____mutmut_2, 
        'xǁ_ComplementSetǁ__ior____mutmut_3': xǁ_ComplementSetǁ__ior____mutmut_3, 
        'xǁ_ComplementSetǁ__ior____mutmut_4': xǁ_ComplementSetǁ__ior____mutmut_4, 
        'xǁ_ComplementSetǁ__ior____mutmut_5': xǁ_ComplementSetǁ__ior____mutmut_5, 
        'xǁ_ComplementSetǁ__ior____mutmut_6': xǁ_ComplementSetǁ__ior____mutmut_6, 
        'xǁ_ComplementSetǁ__ior____mutmut_7': xǁ_ComplementSetǁ__ior____mutmut_7, 
        'xǁ_ComplementSetǁ__ior____mutmut_8': xǁ_ComplementSetǁ__ior____mutmut_8, 
        'xǁ_ComplementSetǁ__ior____mutmut_9': xǁ_ComplementSetǁ__ior____mutmut_9, 
        'xǁ_ComplementSetǁ__ior____mutmut_10': xǁ_ComplementSetǁ__ior____mutmut_10, 
        'xǁ_ComplementSetǁ__ior____mutmut_11': xǁ_ComplementSetǁ__ior____mutmut_11, 
        'xǁ_ComplementSetǁ__ior____mutmut_12': xǁ_ComplementSetǁ__ior____mutmut_12, 
        'xǁ_ComplementSetǁ__ior____mutmut_13': xǁ_ComplementSetǁ__ior____mutmut_13, 
        'xǁ_ComplementSetǁ__ior____mutmut_14': xǁ_ComplementSetǁ__ior____mutmut_14
    }
    
    def __ior__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__ior____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__ior____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ior__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__ior____mutmut_orig)
    xǁ_ComplementSetǁ__ior____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__ior__'

    def xǁ_ComplementSetǁupdate__mutmut_orig(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_1(self, items):
        if type(None) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_2(self, items):
        if type(items) not in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_3(self, items):
        if type(items) in (set, frozenset):
            inc, exc = None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_4(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(None) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_5(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is not _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_6(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = None
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_7(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_8(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(None), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_9(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is not None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_10(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is not None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_11(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_12(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_13(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(None)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_14(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is not None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_15(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included = exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_16(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_17(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None
            else:  # + +
                self._included.update(inc)

    def xǁ_ComplementSetǁupdate__mutmut_18(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.discard(exc)
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._excluded
            else:  # + +
                self._included.update(None)
    
    xǁ_ComplementSetǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁupdate__mutmut_1': xǁ_ComplementSetǁupdate__mutmut_1, 
        'xǁ_ComplementSetǁupdate__mutmut_2': xǁ_ComplementSetǁupdate__mutmut_2, 
        'xǁ_ComplementSetǁupdate__mutmut_3': xǁ_ComplementSetǁupdate__mutmut_3, 
        'xǁ_ComplementSetǁupdate__mutmut_4': xǁ_ComplementSetǁupdate__mutmut_4, 
        'xǁ_ComplementSetǁupdate__mutmut_5': xǁ_ComplementSetǁupdate__mutmut_5, 
        'xǁ_ComplementSetǁupdate__mutmut_6': xǁ_ComplementSetǁupdate__mutmut_6, 
        'xǁ_ComplementSetǁupdate__mutmut_7': xǁ_ComplementSetǁupdate__mutmut_7, 
        'xǁ_ComplementSetǁupdate__mutmut_8': xǁ_ComplementSetǁupdate__mutmut_8, 
        'xǁ_ComplementSetǁupdate__mutmut_9': xǁ_ComplementSetǁupdate__mutmut_9, 
        'xǁ_ComplementSetǁupdate__mutmut_10': xǁ_ComplementSetǁupdate__mutmut_10, 
        'xǁ_ComplementSetǁupdate__mutmut_11': xǁ_ComplementSetǁupdate__mutmut_11, 
        'xǁ_ComplementSetǁupdate__mutmut_12': xǁ_ComplementSetǁupdate__mutmut_12, 
        'xǁ_ComplementSetǁupdate__mutmut_13': xǁ_ComplementSetǁupdate__mutmut_13, 
        'xǁ_ComplementSetǁupdate__mutmut_14': xǁ_ComplementSetǁupdate__mutmut_14, 
        'xǁ_ComplementSetǁupdate__mutmut_15': xǁ_ComplementSetǁupdate__mutmut_15, 
        'xǁ_ComplementSetǁupdate__mutmut_16': xǁ_ComplementSetǁupdate__mutmut_16, 
        'xǁ_ComplementSetǁupdate__mutmut_17': xǁ_ComplementSetǁupdate__mutmut_17, 
        'xǁ_ComplementSetǁupdate__mutmut_18': xǁ_ComplementSetǁupdate__mutmut_18
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁ_ComplementSetǁupdate__mutmut_orig)
    xǁ_ComplementSetǁupdate__mutmut_orig.__name__ = 'xǁ_ComplementSetǁupdate'

    def xǁ_ComplementSetǁdiscard__mutmut_orig(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_1(self, items):
        if type(None) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_2(self, items):
        if type(items) not in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_3(self, items):
        if type(items) in (set, frozenset):
            inc, exc = None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_4(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(None) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_5(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is not _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_6(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = None
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_7(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_8(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(None), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_9(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is not None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_10(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is not None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_11(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(None)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_12(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_13(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc + self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_14(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is not None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_15(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included = exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_16(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
            else:  # + +
                self._included.discard(inc)

    def xǁ_ComplementSetǁdiscard__mutmut_17(self, items):
        if type(items) in (set, frozenset):
            inc, exc = items, None
        elif type(items) is _ComplementSet:
            inc, exc = items._included, items._excluded
        else:
            inc, exc = frozenset(items), None
        if self._included is None:
            if exc is None:  # - +
                self._excluded.update(inc)
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.discard(None)
    
    xǁ_ComplementSetǁdiscard__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁdiscard__mutmut_1': xǁ_ComplementSetǁdiscard__mutmut_1, 
        'xǁ_ComplementSetǁdiscard__mutmut_2': xǁ_ComplementSetǁdiscard__mutmut_2, 
        'xǁ_ComplementSetǁdiscard__mutmut_3': xǁ_ComplementSetǁdiscard__mutmut_3, 
        'xǁ_ComplementSetǁdiscard__mutmut_4': xǁ_ComplementSetǁdiscard__mutmut_4, 
        'xǁ_ComplementSetǁdiscard__mutmut_5': xǁ_ComplementSetǁdiscard__mutmut_5, 
        'xǁ_ComplementSetǁdiscard__mutmut_6': xǁ_ComplementSetǁdiscard__mutmut_6, 
        'xǁ_ComplementSetǁdiscard__mutmut_7': xǁ_ComplementSetǁdiscard__mutmut_7, 
        'xǁ_ComplementSetǁdiscard__mutmut_8': xǁ_ComplementSetǁdiscard__mutmut_8, 
        'xǁ_ComplementSetǁdiscard__mutmut_9': xǁ_ComplementSetǁdiscard__mutmut_9, 
        'xǁ_ComplementSetǁdiscard__mutmut_10': xǁ_ComplementSetǁdiscard__mutmut_10, 
        'xǁ_ComplementSetǁdiscard__mutmut_11': xǁ_ComplementSetǁdiscard__mutmut_11, 
        'xǁ_ComplementSetǁdiscard__mutmut_12': xǁ_ComplementSetǁdiscard__mutmut_12, 
        'xǁ_ComplementSetǁdiscard__mutmut_13': xǁ_ComplementSetǁdiscard__mutmut_13, 
        'xǁ_ComplementSetǁdiscard__mutmut_14': xǁ_ComplementSetǁdiscard__mutmut_14, 
        'xǁ_ComplementSetǁdiscard__mutmut_15': xǁ_ComplementSetǁdiscard__mutmut_15, 
        'xǁ_ComplementSetǁdiscard__mutmut_16': xǁ_ComplementSetǁdiscard__mutmut_16, 
        'xǁ_ComplementSetǁdiscard__mutmut_17': xǁ_ComplementSetǁdiscard__mutmut_17
    }
    
    def discard(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁdiscard__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁdiscard__mutmut_mutants"), args, kwargs, self)
        return result 
    
    discard.__signature__ = _mutmut_signature(xǁ_ComplementSetǁdiscard__mutmut_orig)
    xǁ_ComplementSetǁdiscard__mutmut_orig.__name__ = 'xǁ_ComplementSetǁdiscard'

    def xǁ_ComplementSetǁsymmetric_difference__mutmut_orig(self, other):
        try:
            return self ^ other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁsymmetric_difference__mutmut_1(self, other):
        try:
            return self & other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁsymmetric_difference__mutmut_2(self, other):
        try:
            return self ^ other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁsymmetric_difference__mutmut_3(self, other):
        try:
            return self ^ other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁsymmetric_difference__mutmut_4(self, other):
        try:
            return self ^ other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁsymmetric_difference__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁsymmetric_difference__mutmut_1': xǁ_ComplementSetǁsymmetric_difference__mutmut_1, 
        'xǁ_ComplementSetǁsymmetric_difference__mutmut_2': xǁ_ComplementSetǁsymmetric_difference__mutmut_2, 
        'xǁ_ComplementSetǁsymmetric_difference__mutmut_3': xǁ_ComplementSetǁsymmetric_difference__mutmut_3, 
        'xǁ_ComplementSetǁsymmetric_difference__mutmut_4': xǁ_ComplementSetǁsymmetric_difference__mutmut_4
    }
    
    def symmetric_difference(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁsymmetric_difference__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁsymmetric_difference__mutmut_mutants"), args, kwargs, self)
        return result 
    
    symmetric_difference.__signature__ = _mutmut_signature(xǁ_ComplementSetǁsymmetric_difference__mutmut_orig)
    xǁ_ComplementSetǁsymmetric_difference__mutmut_orig.__name__ = 'xǁ_ComplementSetǁsymmetric_difference'

    def xǁ_ComplementSetǁ__xor____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=None)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded + inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=None)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(None))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is not None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=None)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc + self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(inc))

    def xǁ_ComplementSetǁ__xor____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=None)

    def xǁ_ComplementSetǁ__xor____mutmut_15(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded - inc)
            else:  # - -
                return _ComplementSet(included=self._excluded.symmetric_difference(exc))
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc - self._included)
            else:  # + +
                return _ComplementSet(included=self._included.symmetric_difference(None))
    
    xǁ_ComplementSetǁ__xor____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__xor____mutmut_1': xǁ_ComplementSetǁ__xor____mutmut_1, 
        'xǁ_ComplementSetǁ__xor____mutmut_2': xǁ_ComplementSetǁ__xor____mutmut_2, 
        'xǁ_ComplementSetǁ__xor____mutmut_3': xǁ_ComplementSetǁ__xor____mutmut_3, 
        'xǁ_ComplementSetǁ__xor____mutmut_4': xǁ_ComplementSetǁ__xor____mutmut_4, 
        'xǁ_ComplementSetǁ__xor____mutmut_5': xǁ_ComplementSetǁ__xor____mutmut_5, 
        'xǁ_ComplementSetǁ__xor____mutmut_6': xǁ_ComplementSetǁ__xor____mutmut_6, 
        'xǁ_ComplementSetǁ__xor____mutmut_7': xǁ_ComplementSetǁ__xor____mutmut_7, 
        'xǁ_ComplementSetǁ__xor____mutmut_8': xǁ_ComplementSetǁ__xor____mutmut_8, 
        'xǁ_ComplementSetǁ__xor____mutmut_9': xǁ_ComplementSetǁ__xor____mutmut_9, 
        'xǁ_ComplementSetǁ__xor____mutmut_10': xǁ_ComplementSetǁ__xor____mutmut_10, 
        'xǁ_ComplementSetǁ__xor____mutmut_11': xǁ_ComplementSetǁ__xor____mutmut_11, 
        'xǁ_ComplementSetǁ__xor____mutmut_12': xǁ_ComplementSetǁ__xor____mutmut_12, 
        'xǁ_ComplementSetǁ__xor____mutmut_13': xǁ_ComplementSetǁ__xor____mutmut_13, 
        'xǁ_ComplementSetǁ__xor____mutmut_14': xǁ_ComplementSetǁ__xor____mutmut_14, 
        'xǁ_ComplementSetǁ__xor____mutmut_15': xǁ_ComplementSetǁ__xor____mutmut_15
    }
    
    def __xor__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__xor____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__xor____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __xor__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__xor____mutmut_orig)
    xǁ_ComplementSetǁ__xor____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__xor__'

    __rxor__ = __xor__

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_orig(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_1(self, other):
        inc, exc = None
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_2(self, other):
        inc, exc = _norm_args_typeerror(None)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_3(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is not None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_4(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is not None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_5(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_6(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_7(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(None)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_8(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_9(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is not None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_10(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included = exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_11(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_12(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None
            else:  # + +
                self._included.symmetric_difference_update(inc)

    def xǁ_ComplementSetǁsymmetric_difference_update__mutmut_13(self, other):
        inc, exc = _norm_args_typeerror(other)
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._excluded.symmetric_difference_update(exc)
                self._included, self._excluded = self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
                self._included, self._excluded = None, self._included
            else:  # + +
                self._included.symmetric_difference_update(None)
    
    xǁ_ComplementSetǁsymmetric_difference_update__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_1': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_1, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_2': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_2, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_3': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_3, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_4': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_4, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_5': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_5, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_6': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_6, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_7': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_7, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_8': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_8, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_9': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_9, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_10': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_10, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_11': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_11, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_12': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_12, 
        'xǁ_ComplementSetǁsymmetric_difference_update__mutmut_13': xǁ_ComplementSetǁsymmetric_difference_update__mutmut_13
    }
    
    def symmetric_difference_update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁsymmetric_difference_update__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁsymmetric_difference_update__mutmut_mutants"), args, kwargs, self)
        return result 
    
    symmetric_difference_update.__signature__ = _mutmut_signature(xǁ_ComplementSetǁsymmetric_difference_update__mutmut_orig)
    xǁ_ComplementSetǁsymmetric_difference_update__mutmut_orig.__name__ = 'xǁ_ComplementSetǁsymmetric_difference_update'

    def xǁ_ComplementSetǁisdisjoint__mutmut_orig(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_2(self, other):
        inc, exc = _norm_args_typeerror(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_3(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_4(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_5(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_6(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(None)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_7(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return True
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_8(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is not None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_9(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(None)
            else:  # + +
                return self._included.isdisjoint(inc)

    def xǁ_ComplementSetǁisdisjoint__mutmut_10(self, other):
        inc, exc = _norm_args_typeerror(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return inc.issubset(self._excluded)
            else:  # - -
                return False
        else:
            if inc is None:  # + -
                return self._included.issubset(exc)
            else:  # + +
                return self._included.isdisjoint(None)
    
    xǁ_ComplementSetǁisdisjoint__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁisdisjoint__mutmut_1': xǁ_ComplementSetǁisdisjoint__mutmut_1, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_2': xǁ_ComplementSetǁisdisjoint__mutmut_2, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_3': xǁ_ComplementSetǁisdisjoint__mutmut_3, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_4': xǁ_ComplementSetǁisdisjoint__mutmut_4, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_5': xǁ_ComplementSetǁisdisjoint__mutmut_5, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_6': xǁ_ComplementSetǁisdisjoint__mutmut_6, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_7': xǁ_ComplementSetǁisdisjoint__mutmut_7, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_8': xǁ_ComplementSetǁisdisjoint__mutmut_8, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_9': xǁ_ComplementSetǁisdisjoint__mutmut_9, 
        'xǁ_ComplementSetǁisdisjoint__mutmut_10': xǁ_ComplementSetǁisdisjoint__mutmut_10
    }
    
    def isdisjoint(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁisdisjoint__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁisdisjoint__mutmut_mutants"), args, kwargs, self)
        return result 
    
    isdisjoint.__signature__ = _mutmut_signature(xǁ_ComplementSetǁisdisjoint__mutmut_orig)
    xǁ_ComplementSetǁisdisjoint__mutmut_orig.__name__ = 'xǁ_ComplementSetǁisdisjoint'

    def xǁ_ComplementSetǁissubset__mutmut_orig(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self <= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁissubset__mutmut_1(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self < other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁissubset__mutmut_2(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self <= other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁissubset__mutmut_3(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self <= other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁissubset__mutmut_4(self, other):
        '''everything missing from other is also missing from self'''
        try:
            return self <= other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁissubset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁissubset__mutmut_1': xǁ_ComplementSetǁissubset__mutmut_1, 
        'xǁ_ComplementSetǁissubset__mutmut_2': xǁ_ComplementSetǁissubset__mutmut_2, 
        'xǁ_ComplementSetǁissubset__mutmut_3': xǁ_ComplementSetǁissubset__mutmut_3, 
        'xǁ_ComplementSetǁissubset__mutmut_4': xǁ_ComplementSetǁissubset__mutmut_4
    }
    
    def issubset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁissubset__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁissubset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    issubset.__signature__ = _mutmut_signature(xǁ_ComplementSetǁissubset__mutmut_orig)
    xǁ_ComplementSetǁissubset__mutmut_orig.__name__ = 'xǁ_ComplementSetǁissubset'

    def xǁ_ComplementSetǁ__le____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return True
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(None)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is not None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(None)
            else:  # + +
                return self._included.issubset(inc)

    def xǁ_ComplementSetǁ__le____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded.issupserset(exc)
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included.issubset(None)
    
    xǁ_ComplementSetǁ__le____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__le____mutmut_1': xǁ_ComplementSetǁ__le____mutmut_1, 
        'xǁ_ComplementSetǁ__le____mutmut_2': xǁ_ComplementSetǁ__le____mutmut_2, 
        'xǁ_ComplementSetǁ__le____mutmut_3': xǁ_ComplementSetǁ__le____mutmut_3, 
        'xǁ_ComplementSetǁ__le____mutmut_4': xǁ_ComplementSetǁ__le____mutmut_4, 
        'xǁ_ComplementSetǁ__le____mutmut_5': xǁ_ComplementSetǁ__le____mutmut_5, 
        'xǁ_ComplementSetǁ__le____mutmut_6': xǁ_ComplementSetǁ__le____mutmut_6, 
        'xǁ_ComplementSetǁ__le____mutmut_7': xǁ_ComplementSetǁ__le____mutmut_7, 
        'xǁ_ComplementSetǁ__le____mutmut_8': xǁ_ComplementSetǁ__le____mutmut_8, 
        'xǁ_ComplementSetǁ__le____mutmut_9': xǁ_ComplementSetǁ__le____mutmut_9, 
        'xǁ_ComplementSetǁ__le____mutmut_10': xǁ_ComplementSetǁ__le____mutmut_10, 
        'xǁ_ComplementSetǁ__le____mutmut_11': xǁ_ComplementSetǁ__le____mutmut_11
    }
    
    def __le__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__le____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__le____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __le__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__le____mutmut_orig)
    xǁ_ComplementSetǁ__le____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__le__'

    def xǁ_ComplementSetǁ__lt____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return True
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded >= exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is not None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(None)
            else:  # + +
                return self._included < inc

    def xǁ_ComplementSetǁ__lt____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return False
            else:  # - -
                return self._excluded > exc
        else:
            if inc is None:  # + -
                return self._included.isdisjoint(exc)
            else:  # + +
                return self._included <= inc
    
    xǁ_ComplementSetǁ__lt____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__lt____mutmut_1': xǁ_ComplementSetǁ__lt____mutmut_1, 
        'xǁ_ComplementSetǁ__lt____mutmut_2': xǁ_ComplementSetǁ__lt____mutmut_2, 
        'xǁ_ComplementSetǁ__lt____mutmut_3': xǁ_ComplementSetǁ__lt____mutmut_3, 
        'xǁ_ComplementSetǁ__lt____mutmut_4': xǁ_ComplementSetǁ__lt____mutmut_4, 
        'xǁ_ComplementSetǁ__lt____mutmut_5': xǁ_ComplementSetǁ__lt____mutmut_5, 
        'xǁ_ComplementSetǁ__lt____mutmut_6': xǁ_ComplementSetǁ__lt____mutmut_6, 
        'xǁ_ComplementSetǁ__lt____mutmut_7': xǁ_ComplementSetǁ__lt____mutmut_7, 
        'xǁ_ComplementSetǁ__lt____mutmut_8': xǁ_ComplementSetǁ__lt____mutmut_8, 
        'xǁ_ComplementSetǁ__lt____mutmut_9': xǁ_ComplementSetǁ__lt____mutmut_9, 
        'xǁ_ComplementSetǁ__lt____mutmut_10': xǁ_ComplementSetǁ__lt____mutmut_10, 
        'xǁ_ComplementSetǁ__lt____mutmut_11': xǁ_ComplementSetǁ__lt____mutmut_11
    }
    
    def __lt__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__lt____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__lt____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __lt__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__lt____mutmut_orig)
    xǁ_ComplementSetǁ__lt____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__lt__'

    def xǁ_ComplementSetǁissuperset__mutmut_orig(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self >= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁissuperset__mutmut_1(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self > other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁissuperset__mutmut_2(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self >= other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁissuperset__mutmut_3(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self >= other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁissuperset__mutmut_4(self, other):
        '''everything missing from self is also missing from super'''
        try:
            return self >= other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁissuperset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁissuperset__mutmut_1': xǁ_ComplementSetǁissuperset__mutmut_1, 
        'xǁ_ComplementSetǁissuperset__mutmut_2': xǁ_ComplementSetǁissuperset__mutmut_2, 
        'xǁ_ComplementSetǁissuperset__mutmut_3': xǁ_ComplementSetǁissuperset__mutmut_3, 
        'xǁ_ComplementSetǁissuperset__mutmut_4': xǁ_ComplementSetǁissuperset__mutmut_4
    }
    
    def issuperset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁissuperset__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁissuperset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    issuperset.__signature__ = _mutmut_signature(xǁ_ComplementSetǁissuperset__mutmut_orig)
    xǁ_ComplementSetǁissuperset__mutmut_orig.__name__ = 'xǁ_ComplementSetǁissuperset'

    def xǁ_ComplementSetǁ__ge____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(None)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(None)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is not None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return True
            else:  # + +
                return self._included.issupserset(inc)

    def xǁ_ComplementSetǁ__ge____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded.issubset(exc)
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included.issupserset(None)
    
    xǁ_ComplementSetǁ__ge____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__ge____mutmut_1': xǁ_ComplementSetǁ__ge____mutmut_1, 
        'xǁ_ComplementSetǁ__ge____mutmut_2': xǁ_ComplementSetǁ__ge____mutmut_2, 
        'xǁ_ComplementSetǁ__ge____mutmut_3': xǁ_ComplementSetǁ__ge____mutmut_3, 
        'xǁ_ComplementSetǁ__ge____mutmut_4': xǁ_ComplementSetǁ__ge____mutmut_4, 
        'xǁ_ComplementSetǁ__ge____mutmut_5': xǁ_ComplementSetǁ__ge____mutmut_5, 
        'xǁ_ComplementSetǁ__ge____mutmut_6': xǁ_ComplementSetǁ__ge____mutmut_6, 
        'xǁ_ComplementSetǁ__ge____mutmut_7': xǁ_ComplementSetǁ__ge____mutmut_7, 
        'xǁ_ComplementSetǁ__ge____mutmut_8': xǁ_ComplementSetǁ__ge____mutmut_8, 
        'xǁ_ComplementSetǁ__ge____mutmut_9': xǁ_ComplementSetǁ__ge____mutmut_9, 
        'xǁ_ComplementSetǁ__ge____mutmut_10': xǁ_ComplementSetǁ__ge____mutmut_10, 
        'xǁ_ComplementSetǁ__ge____mutmut_11': xǁ_ComplementSetǁ__ge____mutmut_11
    }
    
    def __ge__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__ge____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__ge____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ge__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__ge____mutmut_orig)
    xǁ_ComplementSetǁ__ge____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__ge__'

    def xǁ_ComplementSetǁ__gt____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(None)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded <= exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is not None:  # + -
                return False
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return True
            else:  # + +
                return self._included > inc

    def xǁ_ComplementSetǁ__gt____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return not self._excluded.intersection(inc)
            else:  # - -
                return self._excluded < exc
        else:
            if inc is None:  # + -
                return False
            else:  # + +
                return self._included >= inc
    
    xǁ_ComplementSetǁ__gt____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__gt____mutmut_1': xǁ_ComplementSetǁ__gt____mutmut_1, 
        'xǁ_ComplementSetǁ__gt____mutmut_2': xǁ_ComplementSetǁ__gt____mutmut_2, 
        'xǁ_ComplementSetǁ__gt____mutmut_3': xǁ_ComplementSetǁ__gt____mutmut_3, 
        'xǁ_ComplementSetǁ__gt____mutmut_4': xǁ_ComplementSetǁ__gt____mutmut_4, 
        'xǁ_ComplementSetǁ__gt____mutmut_5': xǁ_ComplementSetǁ__gt____mutmut_5, 
        'xǁ_ComplementSetǁ__gt____mutmut_6': xǁ_ComplementSetǁ__gt____mutmut_6, 
        'xǁ_ComplementSetǁ__gt____mutmut_7': xǁ_ComplementSetǁ__gt____mutmut_7, 
        'xǁ_ComplementSetǁ__gt____mutmut_8': xǁ_ComplementSetǁ__gt____mutmut_8, 
        'xǁ_ComplementSetǁ__gt____mutmut_9': xǁ_ComplementSetǁ__gt____mutmut_9, 
        'xǁ_ComplementSetǁ__gt____mutmut_10': xǁ_ComplementSetǁ__gt____mutmut_10, 
        'xǁ_ComplementSetǁ__gt____mutmut_11': xǁ_ComplementSetǁ__gt____mutmut_11
    }
    
    def __gt__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__gt____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__gt____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __gt__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__gt____mutmut_orig)
    xǁ_ComplementSetǁ__gt____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__gt__'

    def xǁ_ComplementSetǁdifference__mutmut_orig(self, other):
        try:
            return self - other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁdifference__mutmut_1(self, other):
        try:
            return self + other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁdifference__mutmut_2(self, other):
        try:
            return self - other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁdifference__mutmut_3(self, other):
        try:
            return self - other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁdifference__mutmut_4(self, other):
        try:
            return self - other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁdifference__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁdifference__mutmut_1': xǁ_ComplementSetǁdifference__mutmut_1, 
        'xǁ_ComplementSetǁdifference__mutmut_2': xǁ_ComplementSetǁdifference__mutmut_2, 
        'xǁ_ComplementSetǁdifference__mutmut_3': xǁ_ComplementSetǁdifference__mutmut_3, 
        'xǁ_ComplementSetǁdifference__mutmut_4': xǁ_ComplementSetǁdifference__mutmut_4
    }
    
    def difference(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁdifference__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁdifference__mutmut_mutants"), args, kwargs, self)
        return result 
    
    difference.__signature__ = _mutmut_signature(xǁ_ComplementSetǁdifference__mutmut_orig)
    xǁ_ComplementSetǁdifference__mutmut_orig.__name__ = 'xǁ_ComplementSetǁdifference'

    def xǁ_ComplementSetǁ__sub____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=None)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded & inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=None)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc + self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is not None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=None)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included | exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(inc))

    def xǁ_ComplementSetǁ__sub____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=None)

    def xǁ_ComplementSetǁ__sub____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(excluded=self._excluded | inc)
            else:  # - -
                return _ComplementSet(included=exc - self._excluded)
        else:
            if inc is None:  # + -
                return _ComplementSet(included=self._included & exc)
            else:  # + +
                return _ComplementSet(included=self._included.difference(None))
    
    xǁ_ComplementSetǁ__sub____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__sub____mutmut_1': xǁ_ComplementSetǁ__sub____mutmut_1, 
        'xǁ_ComplementSetǁ__sub____mutmut_2': xǁ_ComplementSetǁ__sub____mutmut_2, 
        'xǁ_ComplementSetǁ__sub____mutmut_3': xǁ_ComplementSetǁ__sub____mutmut_3, 
        'xǁ_ComplementSetǁ__sub____mutmut_4': xǁ_ComplementSetǁ__sub____mutmut_4, 
        'xǁ_ComplementSetǁ__sub____mutmut_5': xǁ_ComplementSetǁ__sub____mutmut_5, 
        'xǁ_ComplementSetǁ__sub____mutmut_6': xǁ_ComplementSetǁ__sub____mutmut_6, 
        'xǁ_ComplementSetǁ__sub____mutmut_7': xǁ_ComplementSetǁ__sub____mutmut_7, 
        'xǁ_ComplementSetǁ__sub____mutmut_8': xǁ_ComplementSetǁ__sub____mutmut_8, 
        'xǁ_ComplementSetǁ__sub____mutmut_9': xǁ_ComplementSetǁ__sub____mutmut_9, 
        'xǁ_ComplementSetǁ__sub____mutmut_10': xǁ_ComplementSetǁ__sub____mutmut_10, 
        'xǁ_ComplementSetǁ__sub____mutmut_11': xǁ_ComplementSetǁ__sub____mutmut_11, 
        'xǁ_ComplementSetǁ__sub____mutmut_12': xǁ_ComplementSetǁ__sub____mutmut_12, 
        'xǁ_ComplementSetǁ__sub____mutmut_13': xǁ_ComplementSetǁ__sub____mutmut_13, 
        'xǁ_ComplementSetǁ__sub____mutmut_14': xǁ_ComplementSetǁ__sub____mutmut_14
    }
    
    def __sub__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__sub____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__sub____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __sub__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__sub____mutmut_orig)
    xǁ_ComplementSetǁ__sub____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__sub__'

    def xǁ_ComplementSetǁ__rsub____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is not None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is not None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=None)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc | self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=None)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded + exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is not None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=None)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc & self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(self._included))

    def xǁ_ComplementSetǁ__rsub____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=None)

    def xǁ_ComplementSetǁ__rsub____mutmut_14(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        # rsub, so the expression being evaluated is "other - self"
        if self._included is None:
            if exc is None:  # - +
                return _ComplementSet(included=inc & self._excluded)
            else:  # - -
                return _ComplementSet(included=self._excluded - exc)
        else:
            if inc is None:  # + -
                return _ComplementSet(excluded=exc | self._included)
            else:  # + +
                return _ComplementSet(included=inc.difference(None))
    
    xǁ_ComplementSetǁ__rsub____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__rsub____mutmut_1': xǁ_ComplementSetǁ__rsub____mutmut_1, 
        'xǁ_ComplementSetǁ__rsub____mutmut_2': xǁ_ComplementSetǁ__rsub____mutmut_2, 
        'xǁ_ComplementSetǁ__rsub____mutmut_3': xǁ_ComplementSetǁ__rsub____mutmut_3, 
        'xǁ_ComplementSetǁ__rsub____mutmut_4': xǁ_ComplementSetǁ__rsub____mutmut_4, 
        'xǁ_ComplementSetǁ__rsub____mutmut_5': xǁ_ComplementSetǁ__rsub____mutmut_5, 
        'xǁ_ComplementSetǁ__rsub____mutmut_6': xǁ_ComplementSetǁ__rsub____mutmut_6, 
        'xǁ_ComplementSetǁ__rsub____mutmut_7': xǁ_ComplementSetǁ__rsub____mutmut_7, 
        'xǁ_ComplementSetǁ__rsub____mutmut_8': xǁ_ComplementSetǁ__rsub____mutmut_8, 
        'xǁ_ComplementSetǁ__rsub____mutmut_9': xǁ_ComplementSetǁ__rsub____mutmut_9, 
        'xǁ_ComplementSetǁ__rsub____mutmut_10': xǁ_ComplementSetǁ__rsub____mutmut_10, 
        'xǁ_ComplementSetǁ__rsub____mutmut_11': xǁ_ComplementSetǁ__rsub____mutmut_11, 
        'xǁ_ComplementSetǁ__rsub____mutmut_12': xǁ_ComplementSetǁ__rsub____mutmut_12, 
        'xǁ_ComplementSetǁ__rsub____mutmut_13': xǁ_ComplementSetǁ__rsub____mutmut_13, 
        'xǁ_ComplementSetǁ__rsub____mutmut_14': xǁ_ComplementSetǁ__rsub____mutmut_14
    }
    
    def __rsub__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__rsub____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__rsub____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __rsub__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__rsub____mutmut_orig)
    xǁ_ComplementSetǁ__rsub____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__rsub__'

    def xǁ_ComplementSetǁdifference_update__mutmut_orig(self, other):
        try:
            self -= other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁdifference_update__mutmut_1(self, other):
        try:
            self = other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁdifference_update__mutmut_2(self, other):
        try:
            self += other
        except NotImplementedError:
            raise TypeError('argument must be another set or complement(set)')

    def xǁ_ComplementSetǁdifference_update__mutmut_3(self, other):
        try:
            self -= other
        except NotImplementedError:
            raise TypeError(None)

    def xǁ_ComplementSetǁdifference_update__mutmut_4(self, other):
        try:
            self -= other
        except NotImplementedError:
            raise TypeError('XXargument must be another set or complement(set)XX')

    def xǁ_ComplementSetǁdifference_update__mutmut_5(self, other):
        try:
            self -= other
        except NotImplementedError:
            raise TypeError('ARGUMENT MUST BE ANOTHER SET OR COMPLEMENT(SET)')
    
    xǁ_ComplementSetǁdifference_update__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁdifference_update__mutmut_1': xǁ_ComplementSetǁdifference_update__mutmut_1, 
        'xǁ_ComplementSetǁdifference_update__mutmut_2': xǁ_ComplementSetǁdifference_update__mutmut_2, 
        'xǁ_ComplementSetǁdifference_update__mutmut_3': xǁ_ComplementSetǁdifference_update__mutmut_3, 
        'xǁ_ComplementSetǁdifference_update__mutmut_4': xǁ_ComplementSetǁdifference_update__mutmut_4, 
        'xǁ_ComplementSetǁdifference_update__mutmut_5': xǁ_ComplementSetǁdifference_update__mutmut_5
    }
    
    def difference_update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁdifference_update__mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁdifference_update__mutmut_mutants"), args, kwargs, self)
        return result 
    
    difference_update.__signature__ = _mutmut_signature(xǁ_ComplementSetǁdifference_update__mutmut_orig)
    xǁ_ComplementSetǁdifference_update__mutmut_orig.__name__ = 'xǁ_ComplementSetǁdifference_update'

    def xǁ_ComplementSetǁ__isub____mutmut_orig(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_1(self, other):
        inc, exc = None
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_2(self, other):
        inc, exc = _norm_args_notimplemented(None)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_3(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is not NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_4(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is not None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_5(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is not None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_6(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded = inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_7(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded &= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_8(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_9(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc + self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_10(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is not None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_11(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included = exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_12(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included |= exc
            else:  # + +
                self._included.difference_update(inc)
        return self

    def xǁ_ComplementSetǁ__isub____mutmut_13(self, other):
        inc, exc = _norm_args_notimplemented(other)
        if inc is NotImplemented:
            return NotImplemented
        if self._included is None:
            if exc is None:  # - +
                self._excluded |= inc
            else:  # - -
                self._included, self._excluded = exc - self._excluded, None
        else:
            if inc is None:  # + -
                self._included &= exc
            else:  # + +
                self._included.difference_update(None)
        return self
    
    xǁ_ComplementSetǁ__isub____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__isub____mutmut_1': xǁ_ComplementSetǁ__isub____mutmut_1, 
        'xǁ_ComplementSetǁ__isub____mutmut_2': xǁ_ComplementSetǁ__isub____mutmut_2, 
        'xǁ_ComplementSetǁ__isub____mutmut_3': xǁ_ComplementSetǁ__isub____mutmut_3, 
        'xǁ_ComplementSetǁ__isub____mutmut_4': xǁ_ComplementSetǁ__isub____mutmut_4, 
        'xǁ_ComplementSetǁ__isub____mutmut_5': xǁ_ComplementSetǁ__isub____mutmut_5, 
        'xǁ_ComplementSetǁ__isub____mutmut_6': xǁ_ComplementSetǁ__isub____mutmut_6, 
        'xǁ_ComplementSetǁ__isub____mutmut_7': xǁ_ComplementSetǁ__isub____mutmut_7, 
        'xǁ_ComplementSetǁ__isub____mutmut_8': xǁ_ComplementSetǁ__isub____mutmut_8, 
        'xǁ_ComplementSetǁ__isub____mutmut_9': xǁ_ComplementSetǁ__isub____mutmut_9, 
        'xǁ_ComplementSetǁ__isub____mutmut_10': xǁ_ComplementSetǁ__isub____mutmut_10, 
        'xǁ_ComplementSetǁ__isub____mutmut_11': xǁ_ComplementSetǁ__isub____mutmut_11, 
        'xǁ_ComplementSetǁ__isub____mutmut_12': xǁ_ComplementSetǁ__isub____mutmut_12, 
        'xǁ_ComplementSetǁ__isub____mutmut_13': xǁ_ComplementSetǁ__isub____mutmut_13
    }
    
    def __isub__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__isub____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__isub____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __isub__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__isub____mutmut_orig)
    xǁ_ComplementSetǁ__isub____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__isub__'

    def xǁ_ComplementSetǁ__eq____mutmut_orig(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_1(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) and (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_2(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included or self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_3(self, other):
        return (
            type(self) is type(other) or self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_4(self, other):
        return (
            type(None) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_5(self, other):
        return (
            type(self) is not type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_6(self, other):
        return (
            type(self) is type(None)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_7(self, other):
        return (
            type(self) is type(other)
            and self._included != other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_8(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded != other._excluded) or (
            type(other) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_9(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) or self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_10(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(None) in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_11(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) not in (set, frozenset) and self._included == other)

    def xǁ_ComplementSetǁ__eq____mutmut_12(self, other):
        return (
            type(self) is type(other)
            and self._included == other._included
            and self._excluded == other._excluded) or (
            type(other) in (set, frozenset) and self._included != other)
    
    xǁ_ComplementSetǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__eq____mutmut_1': xǁ_ComplementSetǁ__eq____mutmut_1, 
        'xǁ_ComplementSetǁ__eq____mutmut_2': xǁ_ComplementSetǁ__eq____mutmut_2, 
        'xǁ_ComplementSetǁ__eq____mutmut_3': xǁ_ComplementSetǁ__eq____mutmut_3, 
        'xǁ_ComplementSetǁ__eq____mutmut_4': xǁ_ComplementSetǁ__eq____mutmut_4, 
        'xǁ_ComplementSetǁ__eq____mutmut_5': xǁ_ComplementSetǁ__eq____mutmut_5, 
        'xǁ_ComplementSetǁ__eq____mutmut_6': xǁ_ComplementSetǁ__eq____mutmut_6, 
        'xǁ_ComplementSetǁ__eq____mutmut_7': xǁ_ComplementSetǁ__eq____mutmut_7, 
        'xǁ_ComplementSetǁ__eq____mutmut_8': xǁ_ComplementSetǁ__eq____mutmut_8, 
        'xǁ_ComplementSetǁ__eq____mutmut_9': xǁ_ComplementSetǁ__eq____mutmut_9, 
        'xǁ_ComplementSetǁ__eq____mutmut_10': xǁ_ComplementSetǁ__eq____mutmut_10, 
        'xǁ_ComplementSetǁ__eq____mutmut_11': xǁ_ComplementSetǁ__eq____mutmut_11, 
        'xǁ_ComplementSetǁ__eq____mutmut_12': xǁ_ComplementSetǁ__eq____mutmut_12
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__eq____mutmut_orig)
    xǁ_ComplementSetǁ__eq____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__eq__'

    def xǁ_ComplementSetǁ__hash____mutmut_orig(self):
        return hash(self._included) ^ hash(self._excluded)

    def xǁ_ComplementSetǁ__hash____mutmut_1(self):
        return hash(self._included) & hash(self._excluded)

    def xǁ_ComplementSetǁ__hash____mutmut_2(self):
        return hash(None) ^ hash(self._excluded)

    def xǁ_ComplementSetǁ__hash____mutmut_3(self):
        return hash(self._included) ^ hash(None)
    
    xǁ_ComplementSetǁ__hash____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__hash____mutmut_1': xǁ_ComplementSetǁ__hash____mutmut_1, 
        'xǁ_ComplementSetǁ__hash____mutmut_2': xǁ_ComplementSetǁ__hash____mutmut_2, 
        'xǁ_ComplementSetǁ__hash____mutmut_3': xǁ_ComplementSetǁ__hash____mutmut_3
    }
    
    def __hash__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__hash____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__hash____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __hash__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__hash____mutmut_orig)
    xǁ_ComplementSetǁ__hash____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__hash__'

    def xǁ_ComplementSetǁ__len____mutmut_orig(self):
        if self._included is not None:
            return len(self._included)
        raise NotImplementedError('complemented sets have undefined length')

    def xǁ_ComplementSetǁ__len____mutmut_1(self):
        if self._included is None:
            return len(self._included)
        raise NotImplementedError('complemented sets have undefined length')

    def xǁ_ComplementSetǁ__len____mutmut_2(self):
        if self._included is not None:
            return len(self._included)
        raise NotImplementedError(None)

    def xǁ_ComplementSetǁ__len____mutmut_3(self):
        if self._included is not None:
            return len(self._included)
        raise NotImplementedError('XXcomplemented sets have undefined lengthXX')

    def xǁ_ComplementSetǁ__len____mutmut_4(self):
        if self._included is not None:
            return len(self._included)
        raise NotImplementedError('COMPLEMENTED SETS HAVE UNDEFINED LENGTH')
    
    xǁ_ComplementSetǁ__len____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__len____mutmut_1': xǁ_ComplementSetǁ__len____mutmut_1, 
        'xǁ_ComplementSetǁ__len____mutmut_2': xǁ_ComplementSetǁ__len____mutmut_2, 
        'xǁ_ComplementSetǁ__len____mutmut_3': xǁ_ComplementSetǁ__len____mutmut_3, 
        'xǁ_ComplementSetǁ__len____mutmut_4': xǁ_ComplementSetǁ__len____mutmut_4
    }
    
    def __len__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__len____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__len____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __len__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__len____mutmut_orig)
    xǁ_ComplementSetǁ__len____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__len__'

    def xǁ_ComplementSetǁ__iter____mutmut_orig(self):
        if self._included is not None:
            return iter(self._included)
        raise NotImplementedError('complemented sets have undefined contents')

    def xǁ_ComplementSetǁ__iter____mutmut_1(self):
        if self._included is None:
            return iter(self._included)
        raise NotImplementedError('complemented sets have undefined contents')

    def xǁ_ComplementSetǁ__iter____mutmut_2(self):
        if self._included is not None:
            return iter(None)
        raise NotImplementedError('complemented sets have undefined contents')

    def xǁ_ComplementSetǁ__iter____mutmut_3(self):
        if self._included is not None:
            return iter(self._included)
        raise NotImplementedError(None)

    def xǁ_ComplementSetǁ__iter____mutmut_4(self):
        if self._included is not None:
            return iter(self._included)
        raise NotImplementedError('XXcomplemented sets have undefined contentsXX')

    def xǁ_ComplementSetǁ__iter____mutmut_5(self):
        if self._included is not None:
            return iter(self._included)
        raise NotImplementedError('COMPLEMENTED SETS HAVE UNDEFINED CONTENTS')
    
    xǁ_ComplementSetǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__iter____mutmut_1': xǁ_ComplementSetǁ__iter____mutmut_1, 
        'xǁ_ComplementSetǁ__iter____mutmut_2': xǁ_ComplementSetǁ__iter____mutmut_2, 
        'xǁ_ComplementSetǁ__iter____mutmut_3': xǁ_ComplementSetǁ__iter____mutmut_3, 
        'xǁ_ComplementSetǁ__iter____mutmut_4': xǁ_ComplementSetǁ__iter____mutmut_4, 
        'xǁ_ComplementSetǁ__iter____mutmut_5': xǁ_ComplementSetǁ__iter____mutmut_5
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__iter____mutmut_orig)
    xǁ_ComplementSetǁ__iter____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__iter__'

    def xǁ_ComplementSetǁ__bool____mutmut_orig(self):
        if self._included is not None:
            return bool(self._included)
        return True

    def xǁ_ComplementSetǁ__bool____mutmut_1(self):
        if self._included is None:
            return bool(self._included)
        return True

    def xǁ_ComplementSetǁ__bool____mutmut_2(self):
        if self._included is not None:
            return bool(None)
        return True

    def xǁ_ComplementSetǁ__bool____mutmut_3(self):
        if self._included is not None:
            return bool(self._included)
        return False
    
    xǁ_ComplementSetǁ__bool____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_ComplementSetǁ__bool____mutmut_1': xǁ_ComplementSetǁ__bool____mutmut_1, 
        'xǁ_ComplementSetǁ__bool____mutmut_2': xǁ_ComplementSetǁ__bool____mutmut_2, 
        'xǁ_ComplementSetǁ__bool____mutmut_3': xǁ_ComplementSetǁ__bool____mutmut_3
    }
    
    def __bool__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_ComplementSetǁ__bool____mutmut_orig"), object.__getattribute__(self, "xǁ_ComplementSetǁ__bool____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __bool__.__signature__ = _mutmut_signature(xǁ_ComplementSetǁ__bool____mutmut_orig)
    xǁ_ComplementSetǁ__bool____mutmut_orig.__name__ = 'xǁ_ComplementSetǁ__bool__'

