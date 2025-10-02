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

"""``cacheutils`` contains consistent implementations of fundamental
cache types. Currently there are two to choose from:

  * :class:`LRI` - Least-recently inserted
  * :class:`LRU` - Least-recently used

Both caches are :class:`dict` subtypes, designed to be as
interchangeable as possible, to facilitate experimentation. A key
practice with performance enhancement with caching is ensuring that
the caching strategy is working. If the cache is constantly missing,
it is just adding more overhead and code complexity. The standard
statistics are:

  * ``hit_count`` - the number of times the queried key has been in
    the cache
  * ``miss_count`` - the number of times a key has been absent and/or
    fetched by the cache
  * ``soft_miss_count`` - the number of times a key has been absent,
    but a default has been provided by the caller, as with
    :meth:`dict.get` and :meth:`dict.setdefault`. Soft misses are a
    subset of misses, so this number is always less than or equal to
    ``miss_count``.

Additionally, ``cacheutils`` provides :class:`ThresholdCounter`, a
cache-like bounded counter useful for online statistics collection.

Learn more about `caching algorithms on Wikipedia
<https://en.wikipedia.org/wiki/Cache_algorithms#Examples>`_.

"""

# TODO: TimedLRI
# TODO: support 0 max_size?


import heapq
import weakref
import itertools
from operator import attrgetter

try:
    from threading import RLock
except Exception:
    class RLock:
        'Dummy reentrant lock for builds without threads'
        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass

_MISSING = object()
_KWARG_MARK = object()

PREV, NEXT, KEY, VALUE = range(4)   # names for the link fields
DEFAULT_MAX_SIZE = 128
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


class LRI(dict):
    """The ``LRI`` implements the basic *Least Recently Inserted* strategy to
    caching. One could also think of this as a ``SizeLimitedDefaultDict``.

    *on_miss* is a callable that accepts the missing key (as opposed
    to :class:`collections.defaultdict`'s "default_factory", which
    accepts no arguments.) Also note that, like the :class:`LRI`,
    the ``LRI`` is instrumented with statistics tracking.

    >>> cap_cache = LRI(max_size=2)
    >>> cap_cache['a'], cap_cache['b'] = 'A', 'B'
    >>> from pprint import pprint as pp
    >>> pp(dict(cap_cache))
    {'a': 'A', 'b': 'B'}
    >>> [cap_cache['b'] for i in range(3)][0]
    'B'
    >>> cap_cache['c'] = 'C'
    >>> print(cap_cache.get('a'))
    None
    >>> cap_cache.hit_count, cap_cache.miss_count, cap_cache.soft_miss_count
    (3, 1, 1)
    """
    def xǁLRIǁ__init____mutmut_orig(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_1(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size < 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_2(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 1:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_3(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError(None)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_4(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' / max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_5(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('XXexpected max_size > 0, not %rXX' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_6(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('EXPECTED MAX_SIZE > 0, NOT %R' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_7(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = None
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_8(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 1
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_9(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = None
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_10(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = None
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_11(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None or not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_12(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_13(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_14(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(None):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_15(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError(None)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_16(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' / on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_17(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('XXexpected on_miss to be a callableXX'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_18(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('EXPECTED ON_MISS TO BE A CALLABLE'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_19(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            'XX (or None), not %rXX' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_20(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or none), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_21(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (OR NONE), NOT %R' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_22(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = None

        if values:
            self.update(values)
    def xǁLRIǁ__init____mutmut_23(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._lock = RLock()
        self._init_ll()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(None)
    
    xǁLRIǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__init____mutmut_1': xǁLRIǁ__init____mutmut_1, 
        'xǁLRIǁ__init____mutmut_2': xǁLRIǁ__init____mutmut_2, 
        'xǁLRIǁ__init____mutmut_3': xǁLRIǁ__init____mutmut_3, 
        'xǁLRIǁ__init____mutmut_4': xǁLRIǁ__init____mutmut_4, 
        'xǁLRIǁ__init____mutmut_5': xǁLRIǁ__init____mutmut_5, 
        'xǁLRIǁ__init____mutmut_6': xǁLRIǁ__init____mutmut_6, 
        'xǁLRIǁ__init____mutmut_7': xǁLRIǁ__init____mutmut_7, 
        'xǁLRIǁ__init____mutmut_8': xǁLRIǁ__init____mutmut_8, 
        'xǁLRIǁ__init____mutmut_9': xǁLRIǁ__init____mutmut_9, 
        'xǁLRIǁ__init____mutmut_10': xǁLRIǁ__init____mutmut_10, 
        'xǁLRIǁ__init____mutmut_11': xǁLRIǁ__init____mutmut_11, 
        'xǁLRIǁ__init____mutmut_12': xǁLRIǁ__init____mutmut_12, 
        'xǁLRIǁ__init____mutmut_13': xǁLRIǁ__init____mutmut_13, 
        'xǁLRIǁ__init____mutmut_14': xǁLRIǁ__init____mutmut_14, 
        'xǁLRIǁ__init____mutmut_15': xǁLRIǁ__init____mutmut_15, 
        'xǁLRIǁ__init____mutmut_16': xǁLRIǁ__init____mutmut_16, 
        'xǁLRIǁ__init____mutmut_17': xǁLRIǁ__init____mutmut_17, 
        'xǁLRIǁ__init____mutmut_18': xǁLRIǁ__init____mutmut_18, 
        'xǁLRIǁ__init____mutmut_19': xǁLRIǁ__init____mutmut_19, 
        'xǁLRIǁ__init____mutmut_20': xǁLRIǁ__init____mutmut_20, 
        'xǁLRIǁ__init____mutmut_21': xǁLRIǁ__init____mutmut_21, 
        'xǁLRIǁ__init____mutmut_22': xǁLRIǁ__init____mutmut_22, 
        'xǁLRIǁ__init____mutmut_23': xǁLRIǁ__init____mutmut_23
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁLRIǁ__init____mutmut_orig)
    xǁLRIǁ__init____mutmut_orig.__name__ = 'xǁLRIǁ__init__'

    # TODO: fromkeys()?

    # linked list manipulation methods.
    #
    # invariants:
    # 1) 'anchor' is the sentinel node in the doubly linked list.  there is
    #    always only one, and its KEY and VALUE are both _MISSING.
    # 2) the most recently accessed node comes immediately before 'anchor'.
    # 3) the least recently accessed node comes immediately after 'anchor'.
    def xǁLRIǁ_init_ll__mutmut_orig(self):
        anchor = []
        anchor[:] = [anchor, anchor, _MISSING, _MISSING]
        # a link lookup table for finding linked list links in O(1)
        # time.
        self._link_lookup = {}
        self._anchor = anchor

    # TODO: fromkeys()?

    # linked list manipulation methods.
    #
    # invariants:
    # 1) 'anchor' is the sentinel node in the doubly linked list.  there is
    #    always only one, and its KEY and VALUE are both _MISSING.
    # 2) the most recently accessed node comes immediately before 'anchor'.
    # 3) the least recently accessed node comes immediately after 'anchor'.
    def xǁLRIǁ_init_ll__mutmut_1(self):
        anchor = None
        anchor[:] = [anchor, anchor, _MISSING, _MISSING]
        # a link lookup table for finding linked list links in O(1)
        # time.
        self._link_lookup = {}
        self._anchor = anchor

    # TODO: fromkeys()?

    # linked list manipulation methods.
    #
    # invariants:
    # 1) 'anchor' is the sentinel node in the doubly linked list.  there is
    #    always only one, and its KEY and VALUE are both _MISSING.
    # 2) the most recently accessed node comes immediately before 'anchor'.
    # 3) the least recently accessed node comes immediately after 'anchor'.
    def xǁLRIǁ_init_ll__mutmut_2(self):
        anchor = []
        anchor[:] = None
        # a link lookup table for finding linked list links in O(1)
        # time.
        self._link_lookup = {}
        self._anchor = anchor

    # TODO: fromkeys()?

    # linked list manipulation methods.
    #
    # invariants:
    # 1) 'anchor' is the sentinel node in the doubly linked list.  there is
    #    always only one, and its KEY and VALUE are both _MISSING.
    # 2) the most recently accessed node comes immediately before 'anchor'.
    # 3) the least recently accessed node comes immediately after 'anchor'.
    def xǁLRIǁ_init_ll__mutmut_3(self):
        anchor = []
        anchor[:] = [anchor, anchor, _MISSING, _MISSING]
        # a link lookup table for finding linked list links in O(1)
        # time.
        self._link_lookup = None
        self._anchor = anchor

    # TODO: fromkeys()?

    # linked list manipulation methods.
    #
    # invariants:
    # 1) 'anchor' is the sentinel node in the doubly linked list.  there is
    #    always only one, and its KEY and VALUE are both _MISSING.
    # 2) the most recently accessed node comes immediately before 'anchor'.
    # 3) the least recently accessed node comes immediately after 'anchor'.
    def xǁLRIǁ_init_ll__mutmut_4(self):
        anchor = []
        anchor[:] = [anchor, anchor, _MISSING, _MISSING]
        # a link lookup table for finding linked list links in O(1)
        # time.
        self._link_lookup = {}
        self._anchor = None
    
    xǁLRIǁ_init_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_init_ll__mutmut_1': xǁLRIǁ_init_ll__mutmut_1, 
        'xǁLRIǁ_init_ll__mutmut_2': xǁLRIǁ_init_ll__mutmut_2, 
        'xǁLRIǁ_init_ll__mutmut_3': xǁLRIǁ_init_ll__mutmut_3, 
        'xǁLRIǁ_init_ll__mutmut_4': xǁLRIǁ_init_ll__mutmut_4
    }
    
    def _init_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_init_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_init_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _init_ll.__signature__ = _mutmut_signature(xǁLRIǁ_init_ll__mutmut_orig)
    xǁLRIǁ_init_ll__mutmut_orig.__name__ = 'xǁLRIǁ_init_ll'

    def xǁLRIǁ_print_ll__mutmut_orig(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(key, val)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_1(self):
        print(None)
        for (key, val) in self._get_flattened_ll():
            print(key, val)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_2(self):
        print('XX***XX')
        for (key, val) in self._get_flattened_ll():
            print(key, val)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_3(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(None, val)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_4(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(key, None)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_5(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(val)
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_6(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(key, )
        print('***')
        return

    def xǁLRIǁ_print_ll__mutmut_7(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(key, val)
        print(None)
        return

    def xǁLRIǁ_print_ll__mutmut_8(self):
        print('***')
        for (key, val) in self._get_flattened_ll():
            print(key, val)
        print('XX***XX')
        return
    
    xǁLRIǁ_print_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_print_ll__mutmut_1': xǁLRIǁ_print_ll__mutmut_1, 
        'xǁLRIǁ_print_ll__mutmut_2': xǁLRIǁ_print_ll__mutmut_2, 
        'xǁLRIǁ_print_ll__mutmut_3': xǁLRIǁ_print_ll__mutmut_3, 
        'xǁLRIǁ_print_ll__mutmut_4': xǁLRIǁ_print_ll__mutmut_4, 
        'xǁLRIǁ_print_ll__mutmut_5': xǁLRIǁ_print_ll__mutmut_5, 
        'xǁLRIǁ_print_ll__mutmut_6': xǁLRIǁ_print_ll__mutmut_6, 
        'xǁLRIǁ_print_ll__mutmut_7': xǁLRIǁ_print_ll__mutmut_7, 
        'xǁLRIǁ_print_ll__mutmut_8': xǁLRIǁ_print_ll__mutmut_8
    }
    
    def _print_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_print_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_print_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _print_ll.__signature__ = _mutmut_signature(xǁLRIǁ_print_ll__mutmut_orig)
    xǁLRIǁ_print_ll__mutmut_orig.__name__ = 'xǁLRIǁ_print_ll'

    def xǁLRIǁ_get_flattened_ll__mutmut_orig(self):
        flattened_list = []
        link = self._anchor
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_1(self):
        flattened_list = None
        link = self._anchor
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_2(self):
        flattened_list = []
        link = None
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_3(self):
        flattened_list = []
        link = self._anchor
        while False:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_4(self):
        flattened_list = []
        link = self._anchor
        while True:
            flattened_list.append(None)
            link = link[NEXT]
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_5(self):
        flattened_list = []
        link = self._anchor
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = None
            if link is self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_6(self):
        flattened_list = []
        link = self._anchor
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is not self._anchor:
                break
        return flattened_list

    def xǁLRIǁ_get_flattened_ll__mutmut_7(self):
        flattened_list = []
        link = self._anchor
        while True:
            flattened_list.append((link[KEY], link[VALUE]))
            link = link[NEXT]
            if link is self._anchor:
                return
        return flattened_list
    
    xǁLRIǁ_get_flattened_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_get_flattened_ll__mutmut_1': xǁLRIǁ_get_flattened_ll__mutmut_1, 
        'xǁLRIǁ_get_flattened_ll__mutmut_2': xǁLRIǁ_get_flattened_ll__mutmut_2, 
        'xǁLRIǁ_get_flattened_ll__mutmut_3': xǁLRIǁ_get_flattened_ll__mutmut_3, 
        'xǁLRIǁ_get_flattened_ll__mutmut_4': xǁLRIǁ_get_flattened_ll__mutmut_4, 
        'xǁLRIǁ_get_flattened_ll__mutmut_5': xǁLRIǁ_get_flattened_ll__mutmut_5, 
        'xǁLRIǁ_get_flattened_ll__mutmut_6': xǁLRIǁ_get_flattened_ll__mutmut_6, 
        'xǁLRIǁ_get_flattened_ll__mutmut_7': xǁLRIǁ_get_flattened_ll__mutmut_7
    }
    
    def _get_flattened_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_get_flattened_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_get_flattened_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_flattened_ll.__signature__ = _mutmut_signature(xǁLRIǁ_get_flattened_ll__mutmut_orig)
    xǁLRIǁ_get_flattened_ll__mutmut_orig.__name__ = 'xǁLRIǁ_get_flattened_ll'

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_orig(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_1(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = None

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_2(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = None
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_3(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = None

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_4(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = None
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_5(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = None
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_6(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = None
        newest[PREV] = second_newest
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_7(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = None
        newest[NEXT] = anchor
        return newest

    def xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_8(self, key):
        # find what will become the newest link. this may raise a
        # KeyError, which is useful to __getitem__ and __setitem__
        newest = self._link_lookup[key]

        # splice out what will become the newest link.
        newest[PREV][NEXT] = newest[NEXT]
        newest[NEXT][PREV] = newest[PREV]

        # move what will become the newest link immediately before
        # anchor (invariant 2)
        anchor = self._anchor
        second_newest = anchor[PREV]
        second_newest[NEXT] = anchor[PREV] = newest
        newest[PREV] = second_newest
        newest[NEXT] = None
        return newest
    
    xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_1': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_1, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_2': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_2, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_3': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_3, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_4': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_4, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_5': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_5, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_6': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_6, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_7': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_7, 
        'xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_8': xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_8
    }
    
    def _get_link_and_move_to_front_of_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_link_and_move_to_front_of_ll.__signature__ = _mutmut_signature(xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_orig)
    xǁLRIǁ_get_link_and_move_to_front_of_ll__mutmut_orig.__name__ = 'xǁLRIǁ_get_link_and_move_to_front_of_ll'

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_orig(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = self._anchor
        second_newest = anchor[PREV]
        newest = [second_newest, anchor, key, value]
        second_newest[NEXT] = anchor[PREV] = newest
        self._link_lookup[key] = newest

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_1(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = None
        second_newest = anchor[PREV]
        newest = [second_newest, anchor, key, value]
        second_newest[NEXT] = anchor[PREV] = newest
        self._link_lookup[key] = newest

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_2(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = self._anchor
        second_newest = None
        newest = [second_newest, anchor, key, value]
        second_newest[NEXT] = anchor[PREV] = newest
        self._link_lookup[key] = newest

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_3(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = self._anchor
        second_newest = anchor[PREV]
        newest = None
        second_newest[NEXT] = anchor[PREV] = newest
        self._link_lookup[key] = newest

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_4(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = self._anchor
        second_newest = anchor[PREV]
        newest = [second_newest, anchor, key, value]
        second_newest[NEXT] = anchor[PREV] = None
        self._link_lookup[key] = newest

    def xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_5(self, key, value):
        # create a new link and place it immediately before anchor
        # (invariant 2).
        anchor = self._anchor
        second_newest = anchor[PREV]
        newest = [second_newest, anchor, key, value]
        second_newest[NEXT] = anchor[PREV] = newest
        self._link_lookup[key] = None
    
    xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_1': xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_1, 
        'xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_2': xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_2, 
        'xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_3': xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_3, 
        'xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_4': xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_4, 
        'xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_5': xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_5
    }
    
    def _set_key_and_add_to_front_of_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_key_and_add_to_front_of_ll.__signature__ = _mutmut_signature(xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_orig)
    xǁLRIǁ_set_key_and_add_to_front_of_ll__mutmut_orig.__name__ = 'xǁLRIǁ_set_key_and_add_to_front_of_ll'

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_orig(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_1(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = None
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_2(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = None
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_3(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = None

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_4(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = None
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_5(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = None
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_6(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = None
        del self._link_lookup[evicted]
        self._link_lookup[key] = oldanchor
        return evicted

    def xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_7(self, key, value):
        # the link after anchor is the oldest in the linked list
        # (invariant 3).  the current anchor becomes a link that holds
        # the newest key, and the oldest link becomes the new anchor
        # (invariant 1).  now the newest link comes before anchor
        # (invariant 2).  no links are moved; only their keys
        # and values are changed.
        oldanchor = self._anchor
        oldanchor[KEY] = key
        oldanchor[VALUE] = value

        self._anchor = anchor = oldanchor[NEXT]
        evicted = anchor[KEY]
        anchor[KEY] = anchor[VALUE] = _MISSING
        del self._link_lookup[evicted]
        self._link_lookup[key] = None
        return evicted
    
    xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_1': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_1, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_2': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_2, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_3': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_3, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_4': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_4, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_5': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_5, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_6': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_6, 
        'xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_7': xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_7
    }
    
    def _set_key_and_evict_last_in_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_key_and_evict_last_in_ll.__signature__ = _mutmut_signature(xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_orig)
    xǁLRIǁ_set_key_and_evict_last_in_ll__mutmut_orig.__name__ = 'xǁLRIǁ_set_key_and_evict_last_in_ll'

    def xǁLRIǁ_remove_from_ll__mutmut_orig(self, key):
        # splice a link out of the list and drop it from our lookup
        # table.
        link = self._link_lookup.pop(key)
        link[PREV][NEXT] = link[NEXT]
        link[NEXT][PREV] = link[PREV]

    def xǁLRIǁ_remove_from_ll__mutmut_1(self, key):
        # splice a link out of the list and drop it from our lookup
        # table.
        link = None
        link[PREV][NEXT] = link[NEXT]
        link[NEXT][PREV] = link[PREV]

    def xǁLRIǁ_remove_from_ll__mutmut_2(self, key):
        # splice a link out of the list and drop it from our lookup
        # table.
        link = self._link_lookup.pop(None)
        link[PREV][NEXT] = link[NEXT]
        link[NEXT][PREV] = link[PREV]

    def xǁLRIǁ_remove_from_ll__mutmut_3(self, key):
        # splice a link out of the list and drop it from our lookup
        # table.
        link = self._link_lookup.pop(key)
        link[PREV][NEXT] = None
        link[NEXT][PREV] = link[PREV]

    def xǁLRIǁ_remove_from_ll__mutmut_4(self, key):
        # splice a link out of the list and drop it from our lookup
        # table.
        link = self._link_lookup.pop(key)
        link[PREV][NEXT] = link[NEXT]
        link[NEXT][PREV] = None
    
    xǁLRIǁ_remove_from_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ_remove_from_ll__mutmut_1': xǁLRIǁ_remove_from_ll__mutmut_1, 
        'xǁLRIǁ_remove_from_ll__mutmut_2': xǁLRIǁ_remove_from_ll__mutmut_2, 
        'xǁLRIǁ_remove_from_ll__mutmut_3': xǁLRIǁ_remove_from_ll__mutmut_3, 
        'xǁLRIǁ_remove_from_ll__mutmut_4': xǁLRIǁ_remove_from_ll__mutmut_4
    }
    
    def _remove_from_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ_remove_from_ll__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ_remove_from_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove_from_ll.__signature__ = _mutmut_signature(xǁLRIǁ_remove_from_ll__mutmut_orig)
    xǁLRIǁ_remove_from_ll__mutmut_orig.__name__ = 'xǁLRIǁ_remove_from_ll'

    def xǁLRIǁ__setitem____mutmut_orig(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_1(self, key, value):
        with self._lock:
            try:
                link = None
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_2(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(None)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_3(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) <= self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_4(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(None, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_5(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, None)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_6(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_7(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, )
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_8(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = None
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_9(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(None, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_10(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, None)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_11(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_12(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, )
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_13(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(None)
            else:
                link[VALUE] = value
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_14(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = None
            super().__setitem__(key, value)
        return

    def xǁLRIǁ__setitem____mutmut_15(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(None, value)
        return

    def xǁLRIǁ__setitem____mutmut_16(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, None)
        return

    def xǁLRIǁ__setitem____mutmut_17(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(value)
        return

    def xǁLRIǁ__setitem____mutmut_18(self, key, value):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                if len(self) < self.max_size:
                    self._set_key_and_add_to_front_of_ll(key, value)
                else:
                    evicted = self._set_key_and_evict_last_in_ll(key, value)
                    super().__delitem__(evicted)
            else:
                link[VALUE] = value
            super().__setitem__(key, )
        return
    
    xǁLRIǁ__setitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__setitem____mutmut_1': xǁLRIǁ__setitem____mutmut_1, 
        'xǁLRIǁ__setitem____mutmut_2': xǁLRIǁ__setitem____mutmut_2, 
        'xǁLRIǁ__setitem____mutmut_3': xǁLRIǁ__setitem____mutmut_3, 
        'xǁLRIǁ__setitem____mutmut_4': xǁLRIǁ__setitem____mutmut_4, 
        'xǁLRIǁ__setitem____mutmut_5': xǁLRIǁ__setitem____mutmut_5, 
        'xǁLRIǁ__setitem____mutmut_6': xǁLRIǁ__setitem____mutmut_6, 
        'xǁLRIǁ__setitem____mutmut_7': xǁLRIǁ__setitem____mutmut_7, 
        'xǁLRIǁ__setitem____mutmut_8': xǁLRIǁ__setitem____mutmut_8, 
        'xǁLRIǁ__setitem____mutmut_9': xǁLRIǁ__setitem____mutmut_9, 
        'xǁLRIǁ__setitem____mutmut_10': xǁLRIǁ__setitem____mutmut_10, 
        'xǁLRIǁ__setitem____mutmut_11': xǁLRIǁ__setitem____mutmut_11, 
        'xǁLRIǁ__setitem____mutmut_12': xǁLRIǁ__setitem____mutmut_12, 
        'xǁLRIǁ__setitem____mutmut_13': xǁLRIǁ__setitem____mutmut_13, 
        'xǁLRIǁ__setitem____mutmut_14': xǁLRIǁ__setitem____mutmut_14, 
        'xǁLRIǁ__setitem____mutmut_15': xǁLRIǁ__setitem____mutmut_15, 
        'xǁLRIǁ__setitem____mutmut_16': xǁLRIǁ__setitem____mutmut_16, 
        'xǁLRIǁ__setitem____mutmut_17': xǁLRIǁ__setitem____mutmut_17, 
        'xǁLRIǁ__setitem____mutmut_18': xǁLRIǁ__setitem____mutmut_18
    }
    
    def __setitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__setitem____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__setitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setitem__.__signature__ = _mutmut_signature(xǁLRIǁ__setitem____mutmut_orig)
    xǁLRIǁ__setitem____mutmut_orig.__name__ = 'xǁLRIǁ__setitem__'

    def xǁLRIǁ__getitem____mutmut_orig(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_1(self, key):
        with self._lock:
            try:
                link = None
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_2(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count = 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_3(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count -= 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_4(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 2
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_5(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_6(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = None
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_7(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(None)
                return ret

            self.hit_count += 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_8(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count = 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_9(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count -= 1
            return link[VALUE]

    def xǁLRIǁ__getitem____mutmut_10(self, key):
        with self._lock:
            try:
                link = self._link_lookup[key]
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 2
            return link[VALUE]
    
    xǁLRIǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__getitem____mutmut_1': xǁLRIǁ__getitem____mutmut_1, 
        'xǁLRIǁ__getitem____mutmut_2': xǁLRIǁ__getitem____mutmut_2, 
        'xǁLRIǁ__getitem____mutmut_3': xǁLRIǁ__getitem____mutmut_3, 
        'xǁLRIǁ__getitem____mutmut_4': xǁLRIǁ__getitem____mutmut_4, 
        'xǁLRIǁ__getitem____mutmut_5': xǁLRIǁ__getitem____mutmut_5, 
        'xǁLRIǁ__getitem____mutmut_6': xǁLRIǁ__getitem____mutmut_6, 
        'xǁLRIǁ__getitem____mutmut_7': xǁLRIǁ__getitem____mutmut_7, 
        'xǁLRIǁ__getitem____mutmut_8': xǁLRIǁ__getitem____mutmut_8, 
        'xǁLRIǁ__getitem____mutmut_9': xǁLRIǁ__getitem____mutmut_9, 
        'xǁLRIǁ__getitem____mutmut_10': xǁLRIǁ__getitem____mutmut_10
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁLRIǁ__getitem____mutmut_orig)
    xǁLRIǁ__getitem____mutmut_orig.__name__ = 'xǁLRIǁ__getitem__'

    def xǁLRIǁget__mutmut_orig(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count += 1
            return default

    def xǁLRIǁget__mutmut_1(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count = 1
            return default

    def xǁLRIǁget__mutmut_2(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count -= 1
            return default

    def xǁLRIǁget__mutmut_3(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count += 2
            return default
    
    xǁLRIǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁget__mutmut_1': xǁLRIǁget__mutmut_1, 
        'xǁLRIǁget__mutmut_2': xǁLRIǁget__mutmut_2, 
        'xǁLRIǁget__mutmut_3': xǁLRIǁget__mutmut_3
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁget__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁLRIǁget__mutmut_orig)
    xǁLRIǁget__mutmut_orig.__name__ = 'xǁLRIǁget'

    def xǁLRIǁ__delitem____mutmut_orig(self, key):
        with self._lock:
            super().__delitem__(key)
            self._remove_from_ll(key)

    def xǁLRIǁ__delitem____mutmut_1(self, key):
        with self._lock:
            super().__delitem__(None)
            self._remove_from_ll(key)

    def xǁLRIǁ__delitem____mutmut_2(self, key):
        with self._lock:
            super().__delitem__(key)
            self._remove_from_ll(None)
    
    xǁLRIǁ__delitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__delitem____mutmut_1': xǁLRIǁ__delitem____mutmut_1, 
        'xǁLRIǁ__delitem____mutmut_2': xǁLRIǁ__delitem____mutmut_2
    }
    
    def __delitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__delitem____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__delitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delitem__.__signature__ = _mutmut_signature(xǁLRIǁ__delitem____mutmut_orig)
    xǁLRIǁ__delitem____mutmut_orig.__name__ = 'xǁLRIǁ__delitem__'

    def xǁLRIǁpop__mutmut_orig(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = super().pop(key)
            except KeyError:
                if default is _MISSING:
                    raise
                ret = default
            else:
                self._remove_from_ll(key)
            return ret

    def xǁLRIǁpop__mutmut_1(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = None
            except KeyError:
                if default is _MISSING:
                    raise
                ret = default
            else:
                self._remove_from_ll(key)
            return ret

    def xǁLRIǁpop__mutmut_2(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = super().pop(None)
            except KeyError:
                if default is _MISSING:
                    raise
                ret = default
            else:
                self._remove_from_ll(key)
            return ret

    def xǁLRIǁpop__mutmut_3(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = super().pop(key)
            except KeyError:
                if default is not _MISSING:
                    raise
                ret = default
            else:
                self._remove_from_ll(key)
            return ret

    def xǁLRIǁpop__mutmut_4(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = super().pop(key)
            except KeyError:
                if default is _MISSING:
                    raise
                ret = None
            else:
                self._remove_from_ll(key)
            return ret

    def xǁLRIǁpop__mutmut_5(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        with self._lock:
            try:
                ret = super().pop(key)
            except KeyError:
                if default is _MISSING:
                    raise
                ret = default
            else:
                self._remove_from_ll(None)
            return ret
    
    xǁLRIǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁpop__mutmut_1': xǁLRIǁpop__mutmut_1, 
        'xǁLRIǁpop__mutmut_2': xǁLRIǁpop__mutmut_2, 
        'xǁLRIǁpop__mutmut_3': xǁLRIǁpop__mutmut_3, 
        'xǁLRIǁpop__mutmut_4': xǁLRIǁpop__mutmut_4, 
        'xǁLRIǁpop__mutmut_5': xǁLRIǁpop__mutmut_5
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁpop__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁLRIǁpop__mutmut_orig)
    xǁLRIǁpop__mutmut_orig.__name__ = 'xǁLRIǁpop'

    def xǁLRIǁpopitem__mutmut_orig(self):
        with self._lock:
            item = super().popitem()
            self._remove_from_ll(item[0])
            return item

    def xǁLRIǁpopitem__mutmut_1(self):
        with self._lock:
            item = None
            self._remove_from_ll(item[0])
            return item

    def xǁLRIǁpopitem__mutmut_2(self):
        with self._lock:
            item = super().popitem()
            self._remove_from_ll(None)
            return item

    def xǁLRIǁpopitem__mutmut_3(self):
        with self._lock:
            item = super().popitem()
            self._remove_from_ll(item[1])
            return item
    
    xǁLRIǁpopitem__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁpopitem__mutmut_1': xǁLRIǁpopitem__mutmut_1, 
        'xǁLRIǁpopitem__mutmut_2': xǁLRIǁpopitem__mutmut_2, 
        'xǁLRIǁpopitem__mutmut_3': xǁLRIǁpopitem__mutmut_3
    }
    
    def popitem(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁpopitem__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁpopitem__mutmut_mutants"), args, kwargs, self)
        return result 
    
    popitem.__signature__ = _mutmut_signature(xǁLRIǁpopitem__mutmut_orig)
    xǁLRIǁpopitem__mutmut_orig.__name__ = 'xǁLRIǁpopitem'

    def clear(self):
        with self._lock:
            super().clear()
            self._init_ll()

    def xǁLRIǁcopy__mutmut_orig(self):
        return self.__class__(max_size=self.max_size, values=self)

    def xǁLRIǁcopy__mutmut_1(self):
        return self.__class__(max_size=None, values=self)

    def xǁLRIǁcopy__mutmut_2(self):
        return self.__class__(max_size=self.max_size, values=None)

    def xǁLRIǁcopy__mutmut_3(self):
        return self.__class__(values=self)

    def xǁLRIǁcopy__mutmut_4(self):
        return self.__class__(max_size=self.max_size, )
    
    xǁLRIǁcopy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁcopy__mutmut_1': xǁLRIǁcopy__mutmut_1, 
        'xǁLRIǁcopy__mutmut_2': xǁLRIǁcopy__mutmut_2, 
        'xǁLRIǁcopy__mutmut_3': xǁLRIǁcopy__mutmut_3, 
        'xǁLRIǁcopy__mutmut_4': xǁLRIǁcopy__mutmut_4
    }
    
    def copy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁcopy__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁcopy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    copy.__signature__ = _mutmut_signature(xǁLRIǁcopy__mutmut_orig)
    xǁLRIǁcopy__mutmut_orig.__name__ = 'xǁLRIǁcopy'

    def xǁLRIǁsetdefault__mutmut_orig(self, key, default=None):
        with self._lock:
            try:
                return self[key]
            except KeyError:
                self.soft_miss_count += 1
                self[key] = default
                return default

    def xǁLRIǁsetdefault__mutmut_1(self, key, default=None):
        with self._lock:
            try:
                return self[key]
            except KeyError:
                self.soft_miss_count = 1
                self[key] = default
                return default

    def xǁLRIǁsetdefault__mutmut_2(self, key, default=None):
        with self._lock:
            try:
                return self[key]
            except KeyError:
                self.soft_miss_count -= 1
                self[key] = default
                return default

    def xǁLRIǁsetdefault__mutmut_3(self, key, default=None):
        with self._lock:
            try:
                return self[key]
            except KeyError:
                self.soft_miss_count += 2
                self[key] = default
                return default

    def xǁLRIǁsetdefault__mutmut_4(self, key, default=None):
        with self._lock:
            try:
                return self[key]
            except KeyError:
                self.soft_miss_count += 1
                self[key] = None
                return default
    
    xǁLRIǁsetdefault__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁsetdefault__mutmut_1': xǁLRIǁsetdefault__mutmut_1, 
        'xǁLRIǁsetdefault__mutmut_2': xǁLRIǁsetdefault__mutmut_2, 
        'xǁLRIǁsetdefault__mutmut_3': xǁLRIǁsetdefault__mutmut_3, 
        'xǁLRIǁsetdefault__mutmut_4': xǁLRIǁsetdefault__mutmut_4
    }
    
    def setdefault(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁsetdefault__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁsetdefault__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setdefault.__signature__ = _mutmut_signature(xǁLRIǁsetdefault__mutmut_orig)
    xǁLRIǁsetdefault__mutmut_orig.__name__ = 'xǁLRIǁsetdefault'

    def xǁLRIǁupdate__mutmut_orig(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_1(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is not self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_2(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = None
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_3(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(None):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_4(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(None, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_5(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, None, None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_6(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr('keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_7(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_8(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', )):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_9(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'XXkeysXX', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_10(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'KEYS', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_11(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(None, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_12(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, None)
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_13(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_14(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, )
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_15(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(None, v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_16(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, None)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_17(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(v)
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_18(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, )
            for k in F:
                setitem(k, F[k])
            return

    def xǁLRIǁupdate__mutmut_19(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(None, F[k])
            return

    def xǁLRIǁupdate__mutmut_20(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, None)
            return

    def xǁLRIǁupdate__mutmut_21(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(F[k])
            return

    def xǁLRIǁupdate__mutmut_22(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        with self._lock:
            if E is self:
                return
            setitem = self.__setitem__
            if callable(getattr(E, 'keys', None)):
                for k in E.keys():
                    setitem(k, E[k])
            else:
                for k, v in E:
                    setitem(k, v)
            for k in F:
                setitem(k, )
            return
    
    xǁLRIǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁupdate__mutmut_1': xǁLRIǁupdate__mutmut_1, 
        'xǁLRIǁupdate__mutmut_2': xǁLRIǁupdate__mutmut_2, 
        'xǁLRIǁupdate__mutmut_3': xǁLRIǁupdate__mutmut_3, 
        'xǁLRIǁupdate__mutmut_4': xǁLRIǁupdate__mutmut_4, 
        'xǁLRIǁupdate__mutmut_5': xǁLRIǁupdate__mutmut_5, 
        'xǁLRIǁupdate__mutmut_6': xǁLRIǁupdate__mutmut_6, 
        'xǁLRIǁupdate__mutmut_7': xǁLRIǁupdate__mutmut_7, 
        'xǁLRIǁupdate__mutmut_8': xǁLRIǁupdate__mutmut_8, 
        'xǁLRIǁupdate__mutmut_9': xǁLRIǁupdate__mutmut_9, 
        'xǁLRIǁupdate__mutmut_10': xǁLRIǁupdate__mutmut_10, 
        'xǁLRIǁupdate__mutmut_11': xǁLRIǁupdate__mutmut_11, 
        'xǁLRIǁupdate__mutmut_12': xǁLRIǁupdate__mutmut_12, 
        'xǁLRIǁupdate__mutmut_13': xǁLRIǁupdate__mutmut_13, 
        'xǁLRIǁupdate__mutmut_14': xǁLRIǁupdate__mutmut_14, 
        'xǁLRIǁupdate__mutmut_15': xǁLRIǁupdate__mutmut_15, 
        'xǁLRIǁupdate__mutmut_16': xǁLRIǁupdate__mutmut_16, 
        'xǁLRIǁupdate__mutmut_17': xǁLRIǁupdate__mutmut_17, 
        'xǁLRIǁupdate__mutmut_18': xǁLRIǁupdate__mutmut_18, 
        'xǁLRIǁupdate__mutmut_19': xǁLRIǁupdate__mutmut_19, 
        'xǁLRIǁupdate__mutmut_20': xǁLRIǁupdate__mutmut_20, 
        'xǁLRIǁupdate__mutmut_21': xǁLRIǁupdate__mutmut_21, 
        'xǁLRIǁupdate__mutmut_22': xǁLRIǁupdate__mutmut_22
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁLRIǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁLRIǁupdate__mutmut_orig)
    xǁLRIǁupdate__mutmut_orig.__name__ = 'xǁLRIǁupdate'

    def xǁLRIǁ__eq____mutmut_orig(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) != len(self):
                return False
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_1(self, other):
        with self._lock:
            if self is not other:
                return True
            if len(other) != len(self):
                return False
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_2(self, other):
        with self._lock:
            if self is other:
                return False
            if len(other) != len(self):
                return False
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_3(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) == len(self):
                return False
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_4(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) != len(self):
                return True
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_5(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) != len(self):
                return False
            if isinstance(other, LRI):
                return other == self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_6(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) != len(self):
                return False
            if not isinstance(other, LRI):
                return other != self
            return super().__eq__(other)

    def xǁLRIǁ__eq____mutmut_7(self, other):
        with self._lock:
            if self is other:
                return True
            if len(other) != len(self):
                return False
            if not isinstance(other, LRI):
                return other == self
            return super().__eq__(None)
    
    xǁLRIǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__eq____mutmut_1': xǁLRIǁ__eq____mutmut_1, 
        'xǁLRIǁ__eq____mutmut_2': xǁLRIǁ__eq____mutmut_2, 
        'xǁLRIǁ__eq____mutmut_3': xǁLRIǁ__eq____mutmut_3, 
        'xǁLRIǁ__eq____mutmut_4': xǁLRIǁ__eq____mutmut_4, 
        'xǁLRIǁ__eq____mutmut_5': xǁLRIǁ__eq____mutmut_5, 
        'xǁLRIǁ__eq____mutmut_6': xǁLRIǁ__eq____mutmut_6, 
        'xǁLRIǁ__eq____mutmut_7': xǁLRIǁ__eq____mutmut_7
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁLRIǁ__eq____mutmut_orig)
    xǁLRIǁ__eq____mutmut_orig.__name__ = 'xǁLRIǁ__eq__'

    def xǁLRIǁ__ne____mutmut_orig(self, other):
        return not (self == other)

    def xǁLRIǁ__ne____mutmut_1(self, other):
        return (self == other)

    def xǁLRIǁ__ne____mutmut_2(self, other):
        return not (self != other)
    
    xǁLRIǁ__ne____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__ne____mutmut_1': xǁLRIǁ__ne____mutmut_1, 
        'xǁLRIǁ__ne____mutmut_2': xǁLRIǁ__ne____mutmut_2
    }
    
    def __ne__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__ne____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__ne____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ne__.__signature__ = _mutmut_signature(xǁLRIǁ__ne____mutmut_orig)
    xǁLRIǁ__ne____mutmut_orig.__name__ = 'xǁLRIǁ__ne__'

    def xǁLRIǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        val_map = super().__repr__()
        return ('%s(max_size=%r, on_miss=%r, values=%s)'
                % (cn, self.max_size, self.on_miss, val_map))

    def xǁLRIǁ__repr____mutmut_1(self):
        cn = None
        val_map = super().__repr__()
        return ('%s(max_size=%r, on_miss=%r, values=%s)'
                % (cn, self.max_size, self.on_miss, val_map))

    def xǁLRIǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        val_map = None
        return ('%s(max_size=%r, on_miss=%r, values=%s)'
                % (cn, self.max_size, self.on_miss, val_map))

    def xǁLRIǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        val_map = super().__repr__()
        return ('%s(max_size=%r, on_miss=%r, values=%s)' / (cn, self.max_size, self.on_miss, val_map))

    def xǁLRIǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        val_map = super().__repr__()
        return ('XX%s(max_size=%r, on_miss=%r, values=%s)XX'
                % (cn, self.max_size, self.on_miss, val_map))

    def xǁLRIǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        val_map = super().__repr__()
        return ('%S(MAX_SIZE=%R, ON_MISS=%R, VALUES=%S)'
                % (cn, self.max_size, self.on_miss, val_map))
    
    xǁLRIǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRIǁ__repr____mutmut_1': xǁLRIǁ__repr____mutmut_1, 
        'xǁLRIǁ__repr____mutmut_2': xǁLRIǁ__repr____mutmut_2, 
        'xǁLRIǁ__repr____mutmut_3': xǁLRIǁ__repr____mutmut_3, 
        'xǁLRIǁ__repr____mutmut_4': xǁLRIǁ__repr____mutmut_4, 
        'xǁLRIǁ__repr____mutmut_5': xǁLRIǁ__repr____mutmut_5
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRIǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁLRIǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁLRIǁ__repr____mutmut_orig)
    xǁLRIǁ__repr____mutmut_orig.__name__ = 'xǁLRIǁ__repr__'


class LRU(LRI):
    """The ``LRU`` is :class:`dict` subtype implementation of the
    *Least-Recently Used* caching strategy.

    Args:
        max_size (int): Max number of items to cache. Defaults to ``128``.
        values (iterable): Initial values for the cache. Defaults to ``None``.
        on_miss (callable): a callable which accepts a single argument, the
            key not present in the cache, and returns the value to be cached.

    >>> cap_cache = LRU(max_size=2)
    >>> cap_cache['a'], cap_cache['b'] = 'A', 'B'
    >>> from pprint import pprint as pp
    >>> pp(dict(cap_cache))
    {'a': 'A', 'b': 'B'}
    >>> [cap_cache['b'] for i in range(3)][0]
    'B'
    >>> cap_cache['c'] = 'C'
    >>> print(cap_cache.get('a'))
    None

    This cache is also instrumented with statistics
    collection. ``hit_count``, ``miss_count``, and ``soft_miss_count``
    are all integer members that can be used to introspect the
    performance of the cache. ("Soft" misses are misses that did not
    raise :exc:`KeyError`, e.g., ``LRU.get()`` or ``on_miss`` was used to
    cache a default.

    >>> cap_cache.hit_count, cap_cache.miss_count, cap_cache.soft_miss_count
    (3, 1, 1)

    Other than the size-limiting caching behavior and statistics,
    ``LRU`` acts like its parent class, the built-in Python :class:`dict`.
    """
    def xǁLRUǁ__getitem____mutmut_orig(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_1(self, key):
        with self._lock:
            try:
                link = None
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_2(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(None)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_3(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count = 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_4(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count -= 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_5(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 2
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_6(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_7(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = None
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_8(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(None)
                return ret

            self.hit_count += 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_9(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count = 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_10(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count -= 1
            return link[VALUE]
    def xǁLRUǁ__getitem____mutmut_11(self, key):
        with self._lock:
            try:
                link = self._get_link_and_move_to_front_of_ll(key)
            except KeyError:
                self.miss_count += 1
                if not self.on_miss:
                    raise
                ret = self[key] = self.on_miss(key)
                return ret

            self.hit_count += 2
            return link[VALUE]
    
    xǁLRUǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLRUǁ__getitem____mutmut_1': xǁLRUǁ__getitem____mutmut_1, 
        'xǁLRUǁ__getitem____mutmut_2': xǁLRUǁ__getitem____mutmut_2, 
        'xǁLRUǁ__getitem____mutmut_3': xǁLRUǁ__getitem____mutmut_3, 
        'xǁLRUǁ__getitem____mutmut_4': xǁLRUǁ__getitem____mutmut_4, 
        'xǁLRUǁ__getitem____mutmut_5': xǁLRUǁ__getitem____mutmut_5, 
        'xǁLRUǁ__getitem____mutmut_6': xǁLRUǁ__getitem____mutmut_6, 
        'xǁLRUǁ__getitem____mutmut_7': xǁLRUǁ__getitem____mutmut_7, 
        'xǁLRUǁ__getitem____mutmut_8': xǁLRUǁ__getitem____mutmut_8, 
        'xǁLRUǁ__getitem____mutmut_9': xǁLRUǁ__getitem____mutmut_9, 
        'xǁLRUǁ__getitem____mutmut_10': xǁLRUǁ__getitem____mutmut_10, 
        'xǁLRUǁ__getitem____mutmut_11': xǁLRUǁ__getitem____mutmut_11
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLRUǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁLRUǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁLRUǁ__getitem____mutmut_orig)
    xǁLRUǁ__getitem____mutmut_orig.__name__ = 'xǁLRUǁ__getitem__'


### Cached decorator
# Key-making technique adapted from Python 3.4's functools

class _HashedKey(list):
    """The _HashedKey guarantees that hash() will be called no more than once
    per cached function invocation.
    """
    __slots__ = 'hash_value'

    def xǁ_HashedKeyǁ__init____mutmut_orig(self, key):
        self[:] = key
        self.hash_value = hash(tuple(key))

    def xǁ_HashedKeyǁ__init____mutmut_1(self, key):
        self[:] = None
        self.hash_value = hash(tuple(key))

    def xǁ_HashedKeyǁ__init____mutmut_2(self, key):
        self[:] = key
        self.hash_value = None

    def xǁ_HashedKeyǁ__init____mutmut_3(self, key):
        self[:] = key
        self.hash_value = hash(None)

    def xǁ_HashedKeyǁ__init____mutmut_4(self, key):
        self[:] = key
        self.hash_value = hash(tuple(None))
    
    xǁ_HashedKeyǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_HashedKeyǁ__init____mutmut_1': xǁ_HashedKeyǁ__init____mutmut_1, 
        'xǁ_HashedKeyǁ__init____mutmut_2': xǁ_HashedKeyǁ__init____mutmut_2, 
        'xǁ_HashedKeyǁ__init____mutmut_3': xǁ_HashedKeyǁ__init____mutmut_3, 
        'xǁ_HashedKeyǁ__init____mutmut_4': xǁ_HashedKeyǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_HashedKeyǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁ_HashedKeyǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁ_HashedKeyǁ__init____mutmut_orig)
    xǁ_HashedKeyǁ__init____mutmut_orig.__name__ = 'xǁ_HashedKeyǁ__init__'

    def __hash__(self):
        return self.hash_value

    def xǁ_HashedKeyǁ__repr____mutmut_orig(self):
        return f'{self.__class__.__name__}({list.__repr__(self)})'

    def xǁ_HashedKeyǁ__repr____mutmut_1(self):
        return f'{self.__class__.__name__}({list.__repr__(None)})'
    
    xǁ_HashedKeyǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_HashedKeyǁ__repr____mutmut_1': xǁ_HashedKeyǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_HashedKeyǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁ_HashedKeyǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁ_HashedKeyǁ__repr____mutmut_orig)
    xǁ_HashedKeyǁ__repr____mutmut_orig.__name__ = 'xǁ_HashedKeyǁ__repr__'


def x_make_cache_key__mutmut_orig(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_1(args, kwargs, typed=True,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_2(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = None
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_3(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(None)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_4(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = None
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_5(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(None)
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_6(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(None)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_7(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(None)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_8(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend(None)
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_9(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(None) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_10(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend(None)
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_11(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(None) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_12(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 or type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_13(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) != 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_14(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 2 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_15(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(None) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_16(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[1]) in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_17(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) not in fasttypes:
        return key[0]
    return _HashedKey(key)


def x_make_cache_key__mutmut_18(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[1]
    return _HashedKey(key)


def x_make_cache_key__mutmut_19(args, kwargs, typed=False,
                   kwarg_mark=_KWARG_MARK,
                   fasttypes=frozenset([int, str, frozenset, type(None)])):
    """Make a generic key from a function's positional and keyword
    arguments, suitable for use in caches. Arguments within *args* and
    *kwargs* must be `hashable`_. If *typed* is ``True``, ``3`` and
    ``3.0`` will be treated as separate keys.

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    >>> tuple(make_cache_key(('a', 'b'), {'c': ('d')}))
    ('a', 'b', _KWARG_MARK, ('c', 'd'))

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable
    """

    # key = [func_name] if func_name else []
    # key.extend(args)
    key = list(args)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key.append(kwarg_mark)
        key.extend(sorted_items)
    if typed:
        key.extend([type(v) for v in args])
        if kwargs:
            key.extend([type(v) for k, v in sorted_items])
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedKey(None)

x_make_cache_key__mutmut_mutants : ClassVar[MutantDict] = {
'x_make_cache_key__mutmut_1': x_make_cache_key__mutmut_1, 
    'x_make_cache_key__mutmut_2': x_make_cache_key__mutmut_2, 
    'x_make_cache_key__mutmut_3': x_make_cache_key__mutmut_3, 
    'x_make_cache_key__mutmut_4': x_make_cache_key__mutmut_4, 
    'x_make_cache_key__mutmut_5': x_make_cache_key__mutmut_5, 
    'x_make_cache_key__mutmut_6': x_make_cache_key__mutmut_6, 
    'x_make_cache_key__mutmut_7': x_make_cache_key__mutmut_7, 
    'x_make_cache_key__mutmut_8': x_make_cache_key__mutmut_8, 
    'x_make_cache_key__mutmut_9': x_make_cache_key__mutmut_9, 
    'x_make_cache_key__mutmut_10': x_make_cache_key__mutmut_10, 
    'x_make_cache_key__mutmut_11': x_make_cache_key__mutmut_11, 
    'x_make_cache_key__mutmut_12': x_make_cache_key__mutmut_12, 
    'x_make_cache_key__mutmut_13': x_make_cache_key__mutmut_13, 
    'x_make_cache_key__mutmut_14': x_make_cache_key__mutmut_14, 
    'x_make_cache_key__mutmut_15': x_make_cache_key__mutmut_15, 
    'x_make_cache_key__mutmut_16': x_make_cache_key__mutmut_16, 
    'x_make_cache_key__mutmut_17': x_make_cache_key__mutmut_17, 
    'x_make_cache_key__mutmut_18': x_make_cache_key__mutmut_18, 
    'x_make_cache_key__mutmut_19': x_make_cache_key__mutmut_19
}

def make_cache_key(*args, **kwargs):
    result = _mutmut_trampoline(x_make_cache_key__mutmut_orig, x_make_cache_key__mutmut_mutants, args, kwargs)
    return result 

make_cache_key.__signature__ = _mutmut_signature(x_make_cache_key__mutmut_orig)
x_make_cache_key__mutmut_orig.__name__ = 'x_make_cache_key'

# for backwards compatibility in case someone was importing it
_make_cache_key = make_cache_key


class CachedFunction:
    """This type is used by :func:`cached`, below. Instances of this
    class are used to wrap functions in caching logic.
    """
    def xǁCachedFunctionǁ__init____mutmut_orig(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_1(self, func, cache, scoped=False, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_2(self, func, cache, scoped=True, typed=True, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_3(self, func, cache, scoped=True, typed=False, key=None):
        self.func = None
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_4(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(None):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_5(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = None
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_6(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_7(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None)) or callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_8(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(None)
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_9(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(None, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_10(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, None, None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_11(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr('__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_12(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_13(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', ))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_14(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, 'XX__getitem__XX', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_15(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__GETITEM__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_16(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(None)):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_17(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(None, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_18(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, None, None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_19(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr('__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_20(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_21(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', ))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_22(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, 'XX__setitem__XX', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_23(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__SETITEM__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_24(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError(None)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_25(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r' / cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_26(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('XXexpected cache to be a dict-like object,XX'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_27(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('EXPECTED CACHE TO BE A DICT-LIKE OBJECT,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_28(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            'XX or callable returning a dict-like object, not %rXX'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_29(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' OR CALLABLE RETURNING A DICT-LIKE OBJECT, NOT %R'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_30(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = None
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_31(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = None
        self.typed = typed
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_32(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = None
        self.key_func = key or make_cache_key
    def xǁCachedFunctionǁ__init____mutmut_33(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = None
    def xǁCachedFunctionǁ__init____mutmut_34(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        if callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be a dict-like object,'
                            ' or callable returning a dict-like object, not %r'
                            % cache)
        else:
            def _get_cache():
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key and make_cache_key
    
    xǁCachedFunctionǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedFunctionǁ__init____mutmut_1': xǁCachedFunctionǁ__init____mutmut_1, 
        'xǁCachedFunctionǁ__init____mutmut_2': xǁCachedFunctionǁ__init____mutmut_2, 
        'xǁCachedFunctionǁ__init____mutmut_3': xǁCachedFunctionǁ__init____mutmut_3, 
        'xǁCachedFunctionǁ__init____mutmut_4': xǁCachedFunctionǁ__init____mutmut_4, 
        'xǁCachedFunctionǁ__init____mutmut_5': xǁCachedFunctionǁ__init____mutmut_5, 
        'xǁCachedFunctionǁ__init____mutmut_6': xǁCachedFunctionǁ__init____mutmut_6, 
        'xǁCachedFunctionǁ__init____mutmut_7': xǁCachedFunctionǁ__init____mutmut_7, 
        'xǁCachedFunctionǁ__init____mutmut_8': xǁCachedFunctionǁ__init____mutmut_8, 
        'xǁCachedFunctionǁ__init____mutmut_9': xǁCachedFunctionǁ__init____mutmut_9, 
        'xǁCachedFunctionǁ__init____mutmut_10': xǁCachedFunctionǁ__init____mutmut_10, 
        'xǁCachedFunctionǁ__init____mutmut_11': xǁCachedFunctionǁ__init____mutmut_11, 
        'xǁCachedFunctionǁ__init____mutmut_12': xǁCachedFunctionǁ__init____mutmut_12, 
        'xǁCachedFunctionǁ__init____mutmut_13': xǁCachedFunctionǁ__init____mutmut_13, 
        'xǁCachedFunctionǁ__init____mutmut_14': xǁCachedFunctionǁ__init____mutmut_14, 
        'xǁCachedFunctionǁ__init____mutmut_15': xǁCachedFunctionǁ__init____mutmut_15, 
        'xǁCachedFunctionǁ__init____mutmut_16': xǁCachedFunctionǁ__init____mutmut_16, 
        'xǁCachedFunctionǁ__init____mutmut_17': xǁCachedFunctionǁ__init____mutmut_17, 
        'xǁCachedFunctionǁ__init____mutmut_18': xǁCachedFunctionǁ__init____mutmut_18, 
        'xǁCachedFunctionǁ__init____mutmut_19': xǁCachedFunctionǁ__init____mutmut_19, 
        'xǁCachedFunctionǁ__init____mutmut_20': xǁCachedFunctionǁ__init____mutmut_20, 
        'xǁCachedFunctionǁ__init____mutmut_21': xǁCachedFunctionǁ__init____mutmut_21, 
        'xǁCachedFunctionǁ__init____mutmut_22': xǁCachedFunctionǁ__init____mutmut_22, 
        'xǁCachedFunctionǁ__init____mutmut_23': xǁCachedFunctionǁ__init____mutmut_23, 
        'xǁCachedFunctionǁ__init____mutmut_24': xǁCachedFunctionǁ__init____mutmut_24, 
        'xǁCachedFunctionǁ__init____mutmut_25': xǁCachedFunctionǁ__init____mutmut_25, 
        'xǁCachedFunctionǁ__init____mutmut_26': xǁCachedFunctionǁ__init____mutmut_26, 
        'xǁCachedFunctionǁ__init____mutmut_27': xǁCachedFunctionǁ__init____mutmut_27, 
        'xǁCachedFunctionǁ__init____mutmut_28': xǁCachedFunctionǁ__init____mutmut_28, 
        'xǁCachedFunctionǁ__init____mutmut_29': xǁCachedFunctionǁ__init____mutmut_29, 
        'xǁCachedFunctionǁ__init____mutmut_30': xǁCachedFunctionǁ__init____mutmut_30, 
        'xǁCachedFunctionǁ__init____mutmut_31': xǁCachedFunctionǁ__init____mutmut_31, 
        'xǁCachedFunctionǁ__init____mutmut_32': xǁCachedFunctionǁ__init____mutmut_32, 
        'xǁCachedFunctionǁ__init____mutmut_33': xǁCachedFunctionǁ__init____mutmut_33, 
        'xǁCachedFunctionǁ__init____mutmut_34': xǁCachedFunctionǁ__init____mutmut_34
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedFunctionǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCachedFunctionǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCachedFunctionǁ__init____mutmut_orig)
    xǁCachedFunctionǁ__init____mutmut_orig.__name__ = 'xǁCachedFunctionǁ__init__'

    def xǁCachedFunctionǁ__call____mutmut_orig(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_1(self, *args, **kwargs):
        cache = None
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_2(self, *args, **kwargs):
        cache = self.get_cache()
        key = None
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_3(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(None, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_4(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, None, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_5(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=None)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_6(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_7(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_8(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, )
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_9(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = None
        except KeyError:
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_10(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = None
        return ret

    def xǁCachedFunctionǁ__call____mutmut_11(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(**kwargs)
        return ret

    def xǁCachedFunctionǁ__call____mutmut_12(self, *args, **kwargs):
        cache = self.get_cache()
        key = self.key_func(args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            ret = cache[key] = self.func(*args, )
        return ret
    
    xǁCachedFunctionǁ__call____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedFunctionǁ__call____mutmut_1': xǁCachedFunctionǁ__call____mutmut_1, 
        'xǁCachedFunctionǁ__call____mutmut_2': xǁCachedFunctionǁ__call____mutmut_2, 
        'xǁCachedFunctionǁ__call____mutmut_3': xǁCachedFunctionǁ__call____mutmut_3, 
        'xǁCachedFunctionǁ__call____mutmut_4': xǁCachedFunctionǁ__call____mutmut_4, 
        'xǁCachedFunctionǁ__call____mutmut_5': xǁCachedFunctionǁ__call____mutmut_5, 
        'xǁCachedFunctionǁ__call____mutmut_6': xǁCachedFunctionǁ__call____mutmut_6, 
        'xǁCachedFunctionǁ__call____mutmut_7': xǁCachedFunctionǁ__call____mutmut_7, 
        'xǁCachedFunctionǁ__call____mutmut_8': xǁCachedFunctionǁ__call____mutmut_8, 
        'xǁCachedFunctionǁ__call____mutmut_9': xǁCachedFunctionǁ__call____mutmut_9, 
        'xǁCachedFunctionǁ__call____mutmut_10': xǁCachedFunctionǁ__call____mutmut_10, 
        'xǁCachedFunctionǁ__call____mutmut_11': xǁCachedFunctionǁ__call____mutmut_11, 
        'xǁCachedFunctionǁ__call____mutmut_12': xǁCachedFunctionǁ__call____mutmut_12
    }
    
    def __call__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedFunctionǁ__call____mutmut_orig"), object.__getattribute__(self, "xǁCachedFunctionǁ__call____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __call__.__signature__ = _mutmut_signature(xǁCachedFunctionǁ__call____mutmut_orig)
    xǁCachedFunctionǁ__call____mutmut_orig.__name__ = 'xǁCachedFunctionǁ__call__'

    def xǁCachedFunctionǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        if self.typed or not self.scoped:
            return ("%s(func=%r, scoped=%r, typed=%r)"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_1(self):
        cn = None
        if self.typed or not self.scoped:
            return ("%s(func=%r, scoped=%r, typed=%r)"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        if self.typed and not self.scoped:
            return ("%s(func=%r, scoped=%r, typed=%r)"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        if self.typed or self.scoped:
            return ("%s(func=%r, scoped=%r, typed=%r)"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        if self.typed or not self.scoped:
            return ("%s(func=%r, scoped=%r, typed=%r)" / (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        if self.typed or not self.scoped:
            return ("XX%s(func=%r, scoped=%r, typed=%r)XX"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"

    def xǁCachedFunctionǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        if self.typed or not self.scoped:
            return ("%S(FUNC=%R, SCOPED=%R, TYPED=%R)"
                    % (cn, self.func, self.scoped, self.typed))
        return f"{cn}(func={self.func!r})"
    
    xǁCachedFunctionǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedFunctionǁ__repr____mutmut_1': xǁCachedFunctionǁ__repr____mutmut_1, 
        'xǁCachedFunctionǁ__repr____mutmut_2': xǁCachedFunctionǁ__repr____mutmut_2, 
        'xǁCachedFunctionǁ__repr____mutmut_3': xǁCachedFunctionǁ__repr____mutmut_3, 
        'xǁCachedFunctionǁ__repr____mutmut_4': xǁCachedFunctionǁ__repr____mutmut_4, 
        'xǁCachedFunctionǁ__repr____mutmut_5': xǁCachedFunctionǁ__repr____mutmut_5, 
        'xǁCachedFunctionǁ__repr____mutmut_6': xǁCachedFunctionǁ__repr____mutmut_6
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedFunctionǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁCachedFunctionǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁCachedFunctionǁ__repr____mutmut_orig)
    xǁCachedFunctionǁ__repr____mutmut_orig.__name__ = 'xǁCachedFunctionǁ__repr__'


class CachedMethod:
    """Similar to :class:`CachedFunction`, this type is used by
    :func:`cachedmethod` to wrap methods in caching logic.
    """
    def xǁCachedMethodǁ__init____mutmut_orig(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_1(self, func, cache, scoped=False, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_2(self, func, cache, scoped=True, typed=True, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_3(self, func, cache, scoped=True, typed=False, key=None):
        self.func = None
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_4(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = None
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_5(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(None, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_6(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, None, False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_7(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', None)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_8(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr('__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_9(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_10(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', )
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_11(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, 'XX__isabstractmethod__XX', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_12(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__ISABSTRACTMETHOD__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_13(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', True)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_14(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = None
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_15(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(None)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_16(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(None):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_17(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = None
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_18(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_19(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None)) or callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_20(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(None)
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_21(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(None, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_22(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, None, None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_23(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr('__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_24(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_25(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', ))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_26(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, 'XX__getitem__XX', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_27(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__GETITEM__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_28(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(None)):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_29(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(None, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_30(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, None, None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_31(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr('__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_32(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_33(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', ))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_34(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, 'XX__setitem__XX', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_35(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__SETITEM__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_36(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError(None)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_37(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' / cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_38(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('XXexpected cache to be an attribute name,XX'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_39(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('EXPECTED CACHE TO BE AN ATTRIBUTE NAME,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_40(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            'XX dict-like object, or callable returningXX'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_41(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' DICT-LIKE OBJECT, OR CALLABLE RETURNING'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_42(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            'XX a dict-like object, not %rXX' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_43(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' A DICT-LIKE OBJECT, NOT %R' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_44(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = None
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_45(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = None
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_46(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = None
        self.key_func = key or make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_47(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = None
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_48(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key and make_cache_key
        self.bound_to = None
    def xǁCachedMethodǁ__init____mutmut_49(self, func, cache, scoped=True, typed=False, key=None):
        self.func = func
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        if isinstance(cache, str):
            self.get_cache = attrgetter(cache)
        elif callable(cache):
            self.get_cache = cache
        elif not (callable(getattr(cache, '__getitem__', None))
                  and callable(getattr(cache, '__setitem__', None))):
            raise TypeError('expected cache to be an attribute name,'
                            ' dict-like object, or callable returning'
                            ' a dict-like object, not %r' % cache)
        else:
            def _get_cache(obj):
                return cache
            self.get_cache = _get_cache
        self.scoped = scoped
        self.typed = typed
        self.key_func = key or make_cache_key
        self.bound_to = ""
    
    xǁCachedMethodǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedMethodǁ__init____mutmut_1': xǁCachedMethodǁ__init____mutmut_1, 
        'xǁCachedMethodǁ__init____mutmut_2': xǁCachedMethodǁ__init____mutmut_2, 
        'xǁCachedMethodǁ__init____mutmut_3': xǁCachedMethodǁ__init____mutmut_3, 
        'xǁCachedMethodǁ__init____mutmut_4': xǁCachedMethodǁ__init____mutmut_4, 
        'xǁCachedMethodǁ__init____mutmut_5': xǁCachedMethodǁ__init____mutmut_5, 
        'xǁCachedMethodǁ__init____mutmut_6': xǁCachedMethodǁ__init____mutmut_6, 
        'xǁCachedMethodǁ__init____mutmut_7': xǁCachedMethodǁ__init____mutmut_7, 
        'xǁCachedMethodǁ__init____mutmut_8': xǁCachedMethodǁ__init____mutmut_8, 
        'xǁCachedMethodǁ__init____mutmut_9': xǁCachedMethodǁ__init____mutmut_9, 
        'xǁCachedMethodǁ__init____mutmut_10': xǁCachedMethodǁ__init____mutmut_10, 
        'xǁCachedMethodǁ__init____mutmut_11': xǁCachedMethodǁ__init____mutmut_11, 
        'xǁCachedMethodǁ__init____mutmut_12': xǁCachedMethodǁ__init____mutmut_12, 
        'xǁCachedMethodǁ__init____mutmut_13': xǁCachedMethodǁ__init____mutmut_13, 
        'xǁCachedMethodǁ__init____mutmut_14': xǁCachedMethodǁ__init____mutmut_14, 
        'xǁCachedMethodǁ__init____mutmut_15': xǁCachedMethodǁ__init____mutmut_15, 
        'xǁCachedMethodǁ__init____mutmut_16': xǁCachedMethodǁ__init____mutmut_16, 
        'xǁCachedMethodǁ__init____mutmut_17': xǁCachedMethodǁ__init____mutmut_17, 
        'xǁCachedMethodǁ__init____mutmut_18': xǁCachedMethodǁ__init____mutmut_18, 
        'xǁCachedMethodǁ__init____mutmut_19': xǁCachedMethodǁ__init____mutmut_19, 
        'xǁCachedMethodǁ__init____mutmut_20': xǁCachedMethodǁ__init____mutmut_20, 
        'xǁCachedMethodǁ__init____mutmut_21': xǁCachedMethodǁ__init____mutmut_21, 
        'xǁCachedMethodǁ__init____mutmut_22': xǁCachedMethodǁ__init____mutmut_22, 
        'xǁCachedMethodǁ__init____mutmut_23': xǁCachedMethodǁ__init____mutmut_23, 
        'xǁCachedMethodǁ__init____mutmut_24': xǁCachedMethodǁ__init____mutmut_24, 
        'xǁCachedMethodǁ__init____mutmut_25': xǁCachedMethodǁ__init____mutmut_25, 
        'xǁCachedMethodǁ__init____mutmut_26': xǁCachedMethodǁ__init____mutmut_26, 
        'xǁCachedMethodǁ__init____mutmut_27': xǁCachedMethodǁ__init____mutmut_27, 
        'xǁCachedMethodǁ__init____mutmut_28': xǁCachedMethodǁ__init____mutmut_28, 
        'xǁCachedMethodǁ__init____mutmut_29': xǁCachedMethodǁ__init____mutmut_29, 
        'xǁCachedMethodǁ__init____mutmut_30': xǁCachedMethodǁ__init____mutmut_30, 
        'xǁCachedMethodǁ__init____mutmut_31': xǁCachedMethodǁ__init____mutmut_31, 
        'xǁCachedMethodǁ__init____mutmut_32': xǁCachedMethodǁ__init____mutmut_32, 
        'xǁCachedMethodǁ__init____mutmut_33': xǁCachedMethodǁ__init____mutmut_33, 
        'xǁCachedMethodǁ__init____mutmut_34': xǁCachedMethodǁ__init____mutmut_34, 
        'xǁCachedMethodǁ__init____mutmut_35': xǁCachedMethodǁ__init____mutmut_35, 
        'xǁCachedMethodǁ__init____mutmut_36': xǁCachedMethodǁ__init____mutmut_36, 
        'xǁCachedMethodǁ__init____mutmut_37': xǁCachedMethodǁ__init____mutmut_37, 
        'xǁCachedMethodǁ__init____mutmut_38': xǁCachedMethodǁ__init____mutmut_38, 
        'xǁCachedMethodǁ__init____mutmut_39': xǁCachedMethodǁ__init____mutmut_39, 
        'xǁCachedMethodǁ__init____mutmut_40': xǁCachedMethodǁ__init____mutmut_40, 
        'xǁCachedMethodǁ__init____mutmut_41': xǁCachedMethodǁ__init____mutmut_41, 
        'xǁCachedMethodǁ__init____mutmut_42': xǁCachedMethodǁ__init____mutmut_42, 
        'xǁCachedMethodǁ__init____mutmut_43': xǁCachedMethodǁ__init____mutmut_43, 
        'xǁCachedMethodǁ__init____mutmut_44': xǁCachedMethodǁ__init____mutmut_44, 
        'xǁCachedMethodǁ__init____mutmut_45': xǁCachedMethodǁ__init____mutmut_45, 
        'xǁCachedMethodǁ__init____mutmut_46': xǁCachedMethodǁ__init____mutmut_46, 
        'xǁCachedMethodǁ__init____mutmut_47': xǁCachedMethodǁ__init____mutmut_47, 
        'xǁCachedMethodǁ__init____mutmut_48': xǁCachedMethodǁ__init____mutmut_48, 
        'xǁCachedMethodǁ__init____mutmut_49': xǁCachedMethodǁ__init____mutmut_49
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedMethodǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCachedMethodǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCachedMethodǁ__init____mutmut_orig)
    xǁCachedMethodǁ__init____mutmut_orig.__name__ = 'xǁCachedMethodǁ__init__'

    def xǁCachedMethodǁ__get____mutmut_orig(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_1(self, obj, objtype=None):
        if obj is not None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_2(self, obj, objtype=None):
        if obj is None:
            return self
        cls = None
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_3(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = None
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_4(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(None, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_5(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, None, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_6(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=None,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_7(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=None, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_8(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=None)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_9(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_10(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_11(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, scoped=self.scoped, key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_12(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  key=self.key_func)
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_13(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, )
        ret.bound_to = obj
        return ret

    def xǁCachedMethodǁ__get____mutmut_14(self, obj, objtype=None):
        if obj is None:
            return self
        cls = self.__class__
        ret = cls(self.func, self.get_cache, typed=self.typed,
                  scoped=self.scoped, key=self.key_func)
        ret.bound_to = None
        return ret
    
    xǁCachedMethodǁ__get____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedMethodǁ__get____mutmut_1': xǁCachedMethodǁ__get____mutmut_1, 
        'xǁCachedMethodǁ__get____mutmut_2': xǁCachedMethodǁ__get____mutmut_2, 
        'xǁCachedMethodǁ__get____mutmut_3': xǁCachedMethodǁ__get____mutmut_3, 
        'xǁCachedMethodǁ__get____mutmut_4': xǁCachedMethodǁ__get____mutmut_4, 
        'xǁCachedMethodǁ__get____mutmut_5': xǁCachedMethodǁ__get____mutmut_5, 
        'xǁCachedMethodǁ__get____mutmut_6': xǁCachedMethodǁ__get____mutmut_6, 
        'xǁCachedMethodǁ__get____mutmut_7': xǁCachedMethodǁ__get____mutmut_7, 
        'xǁCachedMethodǁ__get____mutmut_8': xǁCachedMethodǁ__get____mutmut_8, 
        'xǁCachedMethodǁ__get____mutmut_9': xǁCachedMethodǁ__get____mutmut_9, 
        'xǁCachedMethodǁ__get____mutmut_10': xǁCachedMethodǁ__get____mutmut_10, 
        'xǁCachedMethodǁ__get____mutmut_11': xǁCachedMethodǁ__get____mutmut_11, 
        'xǁCachedMethodǁ__get____mutmut_12': xǁCachedMethodǁ__get____mutmut_12, 
        'xǁCachedMethodǁ__get____mutmut_13': xǁCachedMethodǁ__get____mutmut_13, 
        'xǁCachedMethodǁ__get____mutmut_14': xǁCachedMethodǁ__get____mutmut_14
    }
    
    def __get__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedMethodǁ__get____mutmut_orig"), object.__getattribute__(self, "xǁCachedMethodǁ__get____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __get__.__signature__ = _mutmut_signature(xǁCachedMethodǁ__get____mutmut_orig)
    xǁCachedMethodǁ__get____mutmut_orig.__name__ = 'xǁCachedMethodǁ__get__'

    def xǁCachedMethodǁ__call____mutmut_orig(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_1(self, *args, **kwargs):
        obj = None
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_2(self, *args, **kwargs):
        obj = args[1] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_3(self, *args, **kwargs):
        obj = args[0] if self.bound_to is not None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_4(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = None
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_5(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(None)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_6(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = None
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_7(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) - args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_8(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = None
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_9(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(None, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_10(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, None, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_11(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=None)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_12(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_13(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_14(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, )
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_15(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = None
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_16(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_17(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = None
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_18(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) - args
            ret = cache[key] = self.func(*args, **kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_19(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = None
        return ret

    def xǁCachedMethodǁ__call____mutmut_20(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(**kwargs)
        return ret

    def xǁCachedMethodǁ__call____mutmut_21(self, *args, **kwargs):
        obj = args[0] if self.bound_to is None else self.bound_to
        cache = self.get_cache(obj)
        key_args = (self.bound_to, self.func) + args if self.scoped else args
        key = self.key_func(key_args, kwargs, typed=self.typed)
        try:
            ret = cache[key]
        except KeyError:
            if self.bound_to is not None:
                args = (self.bound_to,) + args
            ret = cache[key] = self.func(*args, )
        return ret
    
    xǁCachedMethodǁ__call____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedMethodǁ__call____mutmut_1': xǁCachedMethodǁ__call____mutmut_1, 
        'xǁCachedMethodǁ__call____mutmut_2': xǁCachedMethodǁ__call____mutmut_2, 
        'xǁCachedMethodǁ__call____mutmut_3': xǁCachedMethodǁ__call____mutmut_3, 
        'xǁCachedMethodǁ__call____mutmut_4': xǁCachedMethodǁ__call____mutmut_4, 
        'xǁCachedMethodǁ__call____mutmut_5': xǁCachedMethodǁ__call____mutmut_5, 
        'xǁCachedMethodǁ__call____mutmut_6': xǁCachedMethodǁ__call____mutmut_6, 
        'xǁCachedMethodǁ__call____mutmut_7': xǁCachedMethodǁ__call____mutmut_7, 
        'xǁCachedMethodǁ__call____mutmut_8': xǁCachedMethodǁ__call____mutmut_8, 
        'xǁCachedMethodǁ__call____mutmut_9': xǁCachedMethodǁ__call____mutmut_9, 
        'xǁCachedMethodǁ__call____mutmut_10': xǁCachedMethodǁ__call____mutmut_10, 
        'xǁCachedMethodǁ__call____mutmut_11': xǁCachedMethodǁ__call____mutmut_11, 
        'xǁCachedMethodǁ__call____mutmut_12': xǁCachedMethodǁ__call____mutmut_12, 
        'xǁCachedMethodǁ__call____mutmut_13': xǁCachedMethodǁ__call____mutmut_13, 
        'xǁCachedMethodǁ__call____mutmut_14': xǁCachedMethodǁ__call____mutmut_14, 
        'xǁCachedMethodǁ__call____mutmut_15': xǁCachedMethodǁ__call____mutmut_15, 
        'xǁCachedMethodǁ__call____mutmut_16': xǁCachedMethodǁ__call____mutmut_16, 
        'xǁCachedMethodǁ__call____mutmut_17': xǁCachedMethodǁ__call____mutmut_17, 
        'xǁCachedMethodǁ__call____mutmut_18': xǁCachedMethodǁ__call____mutmut_18, 
        'xǁCachedMethodǁ__call____mutmut_19': xǁCachedMethodǁ__call____mutmut_19, 
        'xǁCachedMethodǁ__call____mutmut_20': xǁCachedMethodǁ__call____mutmut_20, 
        'xǁCachedMethodǁ__call____mutmut_21': xǁCachedMethodǁ__call____mutmut_21
    }
    
    def __call__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedMethodǁ__call____mutmut_orig"), object.__getattribute__(self, "xǁCachedMethodǁ__call____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __call__.__signature__ = _mutmut_signature(xǁCachedMethodǁ__call____mutmut_orig)
    xǁCachedMethodǁ__call____mutmut_orig.__name__ = 'xǁCachedMethodǁ__call__'

    def xǁCachedMethodǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_1(self):
        cn = None
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        args = None
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args = (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args -= (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' / args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_7(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('XX<%s func=%r scoped=%r typed=%r bound_to=%r>XX' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_8(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%S FUNC=%R SCOPED=%R TYPED=%R BOUND_TO=%R>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" % args)

    def xǁCachedMethodǁ__repr____mutmut_9(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%s(func=%r, scoped=%r, typed=%r)" / args)

    def xǁCachedMethodǁ__repr____mutmut_10(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("XX%s(func=%r, scoped=%r, typed=%r)XX" % args)

    def xǁCachedMethodǁ__repr____mutmut_11(self):
        cn = self.__class__.__name__
        args = (cn, self.func, self.scoped, self.typed)
        if self.bound_to is not None:
            args += (self.bound_to,)
            return ('<%s func=%r scoped=%r typed=%r bound_to=%r>' % args)
        return ("%S(FUNC=%R, SCOPED=%R, TYPED=%R)" % args)
    
    xǁCachedMethodǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCachedMethodǁ__repr____mutmut_1': xǁCachedMethodǁ__repr____mutmut_1, 
        'xǁCachedMethodǁ__repr____mutmut_2': xǁCachedMethodǁ__repr____mutmut_2, 
        'xǁCachedMethodǁ__repr____mutmut_3': xǁCachedMethodǁ__repr____mutmut_3, 
        'xǁCachedMethodǁ__repr____mutmut_4': xǁCachedMethodǁ__repr____mutmut_4, 
        'xǁCachedMethodǁ__repr____mutmut_5': xǁCachedMethodǁ__repr____mutmut_5, 
        'xǁCachedMethodǁ__repr____mutmut_6': xǁCachedMethodǁ__repr____mutmut_6, 
        'xǁCachedMethodǁ__repr____mutmut_7': xǁCachedMethodǁ__repr____mutmut_7, 
        'xǁCachedMethodǁ__repr____mutmut_8': xǁCachedMethodǁ__repr____mutmut_8, 
        'xǁCachedMethodǁ__repr____mutmut_9': xǁCachedMethodǁ__repr____mutmut_9, 
        'xǁCachedMethodǁ__repr____mutmut_10': xǁCachedMethodǁ__repr____mutmut_10, 
        'xǁCachedMethodǁ__repr____mutmut_11': xǁCachedMethodǁ__repr____mutmut_11
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCachedMethodǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁCachedMethodǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁCachedMethodǁ__repr____mutmut_orig)
    xǁCachedMethodǁ__repr____mutmut_orig.__name__ = 'xǁCachedMethodǁ__repr__'


def x_cached__mutmut_orig(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_1(cache, scoped=False, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_2(cache, scoped=True, typed=True, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_3(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(None, cache, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_4(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, None, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_5(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=None, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_6(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=None, key=key)
    return cached_func_decorator


def x_cached__mutmut_7(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=typed, key=None)
    return cached_func_decorator


def x_cached__mutmut_8(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(cache, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_9(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, scoped=scoped, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_10(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, typed=typed, key=key)
    return cached_func_decorator


def x_cached__mutmut_11(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, key=key)
    return cached_func_decorator


def x_cached__mutmut_12(cache, scoped=True, typed=False, key=None):
    """Cache any function with the cache object of your choosing. Note
    that the function wrapped should take only `hashable`_ arguments.

    Args:
        cache (Mapping): Any :class:`dict`-like object suitable for
            use as a cache. Instances of the :class:`LRU` and
            :class:`LRI` are good choices, but a plain :class:`dict`
            can work in some cases, as well. This argument can also be
            a callable which accepts no arguments and returns a mapping.
        scoped (bool): Whether the function itself is part of the
            cache key.  ``True`` by default, different functions will
            not read one another's cache entries, but can evict one
            another's results. ``False`` can be useful for certain
            shared cache use cases. More advanced behavior can be
            produced through the *key* argument.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.

    >>> my_cache = LRU()
    >>> @cached(my_cache)
    ... def cached_lower(x):
    ...     return x.lower()
    ...
    >>> cached_lower("CaChInG's FuN AgAiN!")
    "caching's fun again!"
    >>> len(my_cache)
    1

    .. _hashable: https://docs.python.org/2/glossary.html#term-hashable

    """
    def cached_func_decorator(func):
        return CachedFunction(func, cache, scoped=scoped, typed=typed, )
    return cached_func_decorator

x_cached__mutmut_mutants : ClassVar[MutantDict] = {
'x_cached__mutmut_1': x_cached__mutmut_1, 
    'x_cached__mutmut_2': x_cached__mutmut_2, 
    'x_cached__mutmut_3': x_cached__mutmut_3, 
    'x_cached__mutmut_4': x_cached__mutmut_4, 
    'x_cached__mutmut_5': x_cached__mutmut_5, 
    'x_cached__mutmut_6': x_cached__mutmut_6, 
    'x_cached__mutmut_7': x_cached__mutmut_7, 
    'x_cached__mutmut_8': x_cached__mutmut_8, 
    'x_cached__mutmut_9': x_cached__mutmut_9, 
    'x_cached__mutmut_10': x_cached__mutmut_10, 
    'x_cached__mutmut_11': x_cached__mutmut_11, 
    'x_cached__mutmut_12': x_cached__mutmut_12
}

def cached(*args, **kwargs):
    result = _mutmut_trampoline(x_cached__mutmut_orig, x_cached__mutmut_mutants, args, kwargs)
    return result 

cached.__signature__ = _mutmut_signature(x_cached__mutmut_orig)
x_cached__mutmut_orig.__name__ = 'x_cached'


def x_cachedmethod__mutmut_orig(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_1(cache, scoped=False, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_2(cache, scoped=True, typed=True, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_3(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(None, cache, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_4(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, None, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_5(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=None, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_6(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=None, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_7(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=typed, key=None)
    return cached_method_decorator


def x_cachedmethod__mutmut_8(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(cache, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_9(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, scoped=scoped, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_10(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, typed=typed, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_11(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, key=key)
    return cached_method_decorator


def x_cachedmethod__mutmut_12(cache, scoped=True, typed=False, key=None):
    """Similar to :func:`cached`, ``cachedmethod`` is used to cache
    methods based on their arguments, using any :class:`dict`-like
    *cache* object.

    Args:
        cache (str/Mapping/callable): Can be the name of an attribute
            on the instance, any Mapping/:class:`dict`-like object, or
            a callable which returns a Mapping.
        scoped (bool): Whether the method itself and the object it is
            bound to are part of the cache keys. ``True`` by default,
            different methods will not read one another's cache
            results. ``False`` can be useful for certain shared cache
            use cases. More advanced behavior can be produced through
            the *key* arguments.
        typed (bool): Whether to factor argument types into the cache
            check. Default ``False``, setting to ``True`` causes the
            cache keys for ``3`` and ``3.0`` to be considered unequal.
        key (callable): A callable with a signature that matches
            :func:`make_cache_key` that returns a tuple of hashable
            values to be used as the key in the cache.

    >>> class Lowerer(object):
    ...     def __init__(self):
    ...         self.cache = LRI()
    ...
    ...     @cachedmethod('cache')
    ...     def lower(self, text):
    ...         return text.lower()
    ...
    >>> lowerer = Lowerer()
    >>> lowerer.lower('WOW WHO COULD GUESS CACHING COULD BE SO NEAT')
    'wow who could guess caching could be so neat'
    >>> len(lowerer.cache)
    1

    """
    def cached_method_decorator(func):
        return CachedMethod(func, cache, scoped=scoped, typed=typed, )
    return cached_method_decorator

x_cachedmethod__mutmut_mutants : ClassVar[MutantDict] = {
'x_cachedmethod__mutmut_1': x_cachedmethod__mutmut_1, 
    'x_cachedmethod__mutmut_2': x_cachedmethod__mutmut_2, 
    'x_cachedmethod__mutmut_3': x_cachedmethod__mutmut_3, 
    'x_cachedmethod__mutmut_4': x_cachedmethod__mutmut_4, 
    'x_cachedmethod__mutmut_5': x_cachedmethod__mutmut_5, 
    'x_cachedmethod__mutmut_6': x_cachedmethod__mutmut_6, 
    'x_cachedmethod__mutmut_7': x_cachedmethod__mutmut_7, 
    'x_cachedmethod__mutmut_8': x_cachedmethod__mutmut_8, 
    'x_cachedmethod__mutmut_9': x_cachedmethod__mutmut_9, 
    'x_cachedmethod__mutmut_10': x_cachedmethod__mutmut_10, 
    'x_cachedmethod__mutmut_11': x_cachedmethod__mutmut_11, 
    'x_cachedmethod__mutmut_12': x_cachedmethod__mutmut_12
}

def cachedmethod(*args, **kwargs):
    result = _mutmut_trampoline(x_cachedmethod__mutmut_orig, x_cachedmethod__mutmut_mutants, args, kwargs)
    return result 

cachedmethod.__signature__ = _mutmut_signature(x_cachedmethod__mutmut_orig)
x_cachedmethod__mutmut_orig.__name__ = 'x_cachedmethod'


class cachedproperty:
    """The ``cachedproperty`` is used similar to :class:`property`, except
    that the wrapped method is only called once. This is commonly used
    to implement lazy attributes.

    After the property has been accessed, the value is stored on the
    instance itself, using the same name as the cachedproperty. This
    allows the cache to be cleared with :func:`delattr`, or through
    manipulating the object's ``__dict__``.
    """
    def xǁcachedpropertyǁ__init____mutmut_orig(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_1(self, func):
        self.__doc__ = None
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_2(self, func):
        self.__doc__ = getattr(None, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_3(self, func):
        self.__doc__ = getattr(func, None)
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_4(self, func):
        self.__doc__ = getattr('__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_5(self, func):
        self.__doc__ = getattr(func, )
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_6(self, func):
        self.__doc__ = getattr(func, 'XX__doc__XX')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_7(self, func):
        self.__doc__ = getattr(func, '__DOC__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_8(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = None
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_9(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(None, '__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_10(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, None, False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_11(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', None)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_12(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr('__isabstractmethod__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_13(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_14(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', )
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_15(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, 'XX__isabstractmethod__XX', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_16(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__ISABSTRACTMETHOD__', False)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_17(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', True)
        self.func = func
    def xǁcachedpropertyǁ__init____mutmut_18(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = None
    
    xǁcachedpropertyǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁcachedpropertyǁ__init____mutmut_1': xǁcachedpropertyǁ__init____mutmut_1, 
        'xǁcachedpropertyǁ__init____mutmut_2': xǁcachedpropertyǁ__init____mutmut_2, 
        'xǁcachedpropertyǁ__init____mutmut_3': xǁcachedpropertyǁ__init____mutmut_3, 
        'xǁcachedpropertyǁ__init____mutmut_4': xǁcachedpropertyǁ__init____mutmut_4, 
        'xǁcachedpropertyǁ__init____mutmut_5': xǁcachedpropertyǁ__init____mutmut_5, 
        'xǁcachedpropertyǁ__init____mutmut_6': xǁcachedpropertyǁ__init____mutmut_6, 
        'xǁcachedpropertyǁ__init____mutmut_7': xǁcachedpropertyǁ__init____mutmut_7, 
        'xǁcachedpropertyǁ__init____mutmut_8': xǁcachedpropertyǁ__init____mutmut_8, 
        'xǁcachedpropertyǁ__init____mutmut_9': xǁcachedpropertyǁ__init____mutmut_9, 
        'xǁcachedpropertyǁ__init____mutmut_10': xǁcachedpropertyǁ__init____mutmut_10, 
        'xǁcachedpropertyǁ__init____mutmut_11': xǁcachedpropertyǁ__init____mutmut_11, 
        'xǁcachedpropertyǁ__init____mutmut_12': xǁcachedpropertyǁ__init____mutmut_12, 
        'xǁcachedpropertyǁ__init____mutmut_13': xǁcachedpropertyǁ__init____mutmut_13, 
        'xǁcachedpropertyǁ__init____mutmut_14': xǁcachedpropertyǁ__init____mutmut_14, 
        'xǁcachedpropertyǁ__init____mutmut_15': xǁcachedpropertyǁ__init____mutmut_15, 
        'xǁcachedpropertyǁ__init____mutmut_16': xǁcachedpropertyǁ__init____mutmut_16, 
        'xǁcachedpropertyǁ__init____mutmut_17': xǁcachedpropertyǁ__init____mutmut_17, 
        'xǁcachedpropertyǁ__init____mutmut_18': xǁcachedpropertyǁ__init____mutmut_18
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁcachedpropertyǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁcachedpropertyǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁcachedpropertyǁ__init____mutmut_orig)
    xǁcachedpropertyǁ__init____mutmut_orig.__name__ = 'xǁcachedpropertyǁ__init__'

    def xǁcachedpropertyǁ__get____mutmut_orig(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def xǁcachedpropertyǁ__get____mutmut_1(self, obj, objtype=None):
        if obj is not None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def xǁcachedpropertyǁ__get____mutmut_2(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = None
        return value

    def xǁcachedpropertyǁ__get____mutmut_3(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(None)
        return value
    
    xǁcachedpropertyǁ__get____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁcachedpropertyǁ__get____mutmut_1': xǁcachedpropertyǁ__get____mutmut_1, 
        'xǁcachedpropertyǁ__get____mutmut_2': xǁcachedpropertyǁ__get____mutmut_2, 
        'xǁcachedpropertyǁ__get____mutmut_3': xǁcachedpropertyǁ__get____mutmut_3
    }
    
    def __get__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁcachedpropertyǁ__get____mutmut_orig"), object.__getattribute__(self, "xǁcachedpropertyǁ__get____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __get__.__signature__ = _mutmut_signature(xǁcachedpropertyǁ__get____mutmut_orig)
    xǁcachedpropertyǁ__get____mutmut_orig.__name__ = 'xǁcachedpropertyǁ__get__'

    def xǁcachedpropertyǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return f'<{cn} func={self.func}>'

    def xǁcachedpropertyǁ__repr____mutmut_1(self):
        cn = None
        return f'<{cn} func={self.func}>'
    
    xǁcachedpropertyǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁcachedpropertyǁ__repr____mutmut_1': xǁcachedpropertyǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁcachedpropertyǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁcachedpropertyǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁcachedpropertyǁ__repr____mutmut_orig)
    xǁcachedpropertyǁ__repr____mutmut_orig.__name__ = 'xǁcachedpropertyǁ__repr__'


class ThresholdCounter:
    """A **bounded** dict-like Mapping from keys to counts. The
    ThresholdCounter automatically compacts after every (1 /
    *threshold*) additions, maintaining exact counts for any keys
    whose count represents at least a *threshold* ratio of the total
    data. In other words, if a particular key is not present in the
    ThresholdCounter, its count represents less than *threshold* of
    the total data.

    >>> tc = ThresholdCounter(threshold=0.1)
    >>> tc.add(1)
    >>> tc.items()
    [(1, 1)]
    >>> tc.update([2] * 10)
    >>> tc.get(1)
    0
    >>> tc.add(5)
    >>> 5 in tc
    True
    >>> len(list(tc.elements()))
    11

    As you can see above, the API is kept similar to
    :class:`collections.Counter`. The most notable feature omissions
    being that counted items cannot be set directly, uncounted, or
    removed, as this would disrupt the math.

    Use the ThresholdCounter when you need best-effort long-lived
    counts for dynamically-keyed data. Without a bounded datastructure
    such as this one, the dynamic keys often represent a memory leak
    and can impact application reliability. The ThresholdCounter's
    item replacement strategy is fully deterministic and can be
    thought of as *Amortized Least Relevant*. The absolute upper bound
    of keys it will store is *(2/threshold)*, but realistically
    *(1/threshold)* is expected for uniformly random datastreams, and
    one or two orders of magnitude better for real-world data.

    This algorithm is an implementation of the Lossy Counting
    algorithm described in "Approximate Frequency Counts over Data
    Streams" by Manku & Motwani. Hat tip to Kurt Rose for discovery
    and initial implementation.

    """
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_orig(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_1(self, threshold=1.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_2(self, threshold=0.001):
        if 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_3(self, threshold=0.001):
        if not 1 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_4(self, threshold=0.001):
        if not 0 <= threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_5(self, threshold=0.001):
        if not 0 < threshold <= 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_6(self, threshold=0.001):
        if not 0 < threshold < 2:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_7(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError(None)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_8(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r' / threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_9(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('XXexpected threshold between 0 and 1, not: %rXX'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_10(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('EXPECTED THRESHOLD BETWEEN 0 AND 1, NOT: %R'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_11(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = None
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_12(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 1
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_13(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = None
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_14(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = None
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_15(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = None
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_16(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(None)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_17(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 * threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_18(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(2 / threshold)
        self._cur_bucket = 1
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_19(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = None
    # TODO: hit_count/miss_count?
    def xǁThresholdCounterǁ__init____mutmut_20(self, threshold=0.001):
        if not 0 < threshold < 1:
            raise ValueError('expected threshold between 0 and 1, not: %r'
                             % threshold)

        self.total = 0
        self._count_map = {}
        self._threshold = threshold
        self._thresh_count = int(1 / threshold)
        self._cur_bucket = 2
    
    xǁThresholdCounterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁ__init____mutmut_1': xǁThresholdCounterǁ__init____mutmut_1, 
        'xǁThresholdCounterǁ__init____mutmut_2': xǁThresholdCounterǁ__init____mutmut_2, 
        'xǁThresholdCounterǁ__init____mutmut_3': xǁThresholdCounterǁ__init____mutmut_3, 
        'xǁThresholdCounterǁ__init____mutmut_4': xǁThresholdCounterǁ__init____mutmut_4, 
        'xǁThresholdCounterǁ__init____mutmut_5': xǁThresholdCounterǁ__init____mutmut_5, 
        'xǁThresholdCounterǁ__init____mutmut_6': xǁThresholdCounterǁ__init____mutmut_6, 
        'xǁThresholdCounterǁ__init____mutmut_7': xǁThresholdCounterǁ__init____mutmut_7, 
        'xǁThresholdCounterǁ__init____mutmut_8': xǁThresholdCounterǁ__init____mutmut_8, 
        'xǁThresholdCounterǁ__init____mutmut_9': xǁThresholdCounterǁ__init____mutmut_9, 
        'xǁThresholdCounterǁ__init____mutmut_10': xǁThresholdCounterǁ__init____mutmut_10, 
        'xǁThresholdCounterǁ__init____mutmut_11': xǁThresholdCounterǁ__init____mutmut_11, 
        'xǁThresholdCounterǁ__init____mutmut_12': xǁThresholdCounterǁ__init____mutmut_12, 
        'xǁThresholdCounterǁ__init____mutmut_13': xǁThresholdCounterǁ__init____mutmut_13, 
        'xǁThresholdCounterǁ__init____mutmut_14': xǁThresholdCounterǁ__init____mutmut_14, 
        'xǁThresholdCounterǁ__init____mutmut_15': xǁThresholdCounterǁ__init____mutmut_15, 
        'xǁThresholdCounterǁ__init____mutmut_16': xǁThresholdCounterǁ__init____mutmut_16, 
        'xǁThresholdCounterǁ__init____mutmut_17': xǁThresholdCounterǁ__init____mutmut_17, 
        'xǁThresholdCounterǁ__init____mutmut_18': xǁThresholdCounterǁ__init____mutmut_18, 
        'xǁThresholdCounterǁ__init____mutmut_19': xǁThresholdCounterǁ__init____mutmut_19, 
        'xǁThresholdCounterǁ__init____mutmut_20': xǁThresholdCounterǁ__init____mutmut_20
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁThresholdCounterǁ__init____mutmut_orig)
    xǁThresholdCounterǁ__init____mutmut_orig.__name__ = 'xǁThresholdCounterǁ__init__'

    @property
    def threshold(self):
        return self._threshold

    def xǁThresholdCounterǁadd__mutmut_orig(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_1(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total = 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_2(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total -= 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_3(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 2
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_4(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] = 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_5(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] -= 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_6(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][1] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_7(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 2
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_8(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = None

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_9(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [2, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_10(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket + 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_11(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 2]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_12(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total / self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_13(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count != 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_14(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 1:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_15(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = None
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_16(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(None) > self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_17(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) >= self._cur_bucket}
            self._cur_bucket += 1
        return

    def xǁThresholdCounterǁadd__mutmut_18(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket = 1
        return

    def xǁThresholdCounterǁadd__mutmut_19(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket -= 1
        return

    def xǁThresholdCounterǁadd__mutmut_20(self, key):
        """Increment the count of *key* by 1, automatically adding it if it
        does not exist.

        Cache compaction is triggered every *1/threshold* additions.
        """
        self.total += 1
        try:
            self._count_map[key][0] += 1
        except KeyError:
            self._count_map[key] = [1, self._cur_bucket - 1]

        if self.total % self._thresh_count == 0:
            self._count_map = {k: v for k, v in self._count_map.items()
                                    if sum(v) > self._cur_bucket}
            self._cur_bucket += 2
        return
    
    xǁThresholdCounterǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁadd__mutmut_1': xǁThresholdCounterǁadd__mutmut_1, 
        'xǁThresholdCounterǁadd__mutmut_2': xǁThresholdCounterǁadd__mutmut_2, 
        'xǁThresholdCounterǁadd__mutmut_3': xǁThresholdCounterǁadd__mutmut_3, 
        'xǁThresholdCounterǁadd__mutmut_4': xǁThresholdCounterǁadd__mutmut_4, 
        'xǁThresholdCounterǁadd__mutmut_5': xǁThresholdCounterǁadd__mutmut_5, 
        'xǁThresholdCounterǁadd__mutmut_6': xǁThresholdCounterǁadd__mutmut_6, 
        'xǁThresholdCounterǁadd__mutmut_7': xǁThresholdCounterǁadd__mutmut_7, 
        'xǁThresholdCounterǁadd__mutmut_8': xǁThresholdCounterǁadd__mutmut_8, 
        'xǁThresholdCounterǁadd__mutmut_9': xǁThresholdCounterǁadd__mutmut_9, 
        'xǁThresholdCounterǁadd__mutmut_10': xǁThresholdCounterǁadd__mutmut_10, 
        'xǁThresholdCounterǁadd__mutmut_11': xǁThresholdCounterǁadd__mutmut_11, 
        'xǁThresholdCounterǁadd__mutmut_12': xǁThresholdCounterǁadd__mutmut_12, 
        'xǁThresholdCounterǁadd__mutmut_13': xǁThresholdCounterǁadd__mutmut_13, 
        'xǁThresholdCounterǁadd__mutmut_14': xǁThresholdCounterǁadd__mutmut_14, 
        'xǁThresholdCounterǁadd__mutmut_15': xǁThresholdCounterǁadd__mutmut_15, 
        'xǁThresholdCounterǁadd__mutmut_16': xǁThresholdCounterǁadd__mutmut_16, 
        'xǁThresholdCounterǁadd__mutmut_17': xǁThresholdCounterǁadd__mutmut_17, 
        'xǁThresholdCounterǁadd__mutmut_18': xǁThresholdCounterǁadd__mutmut_18, 
        'xǁThresholdCounterǁadd__mutmut_19': xǁThresholdCounterǁadd__mutmut_19, 
        'xǁThresholdCounterǁadd__mutmut_20': xǁThresholdCounterǁadd__mutmut_20
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁadd__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁThresholdCounterǁadd__mutmut_orig)
    xǁThresholdCounterǁadd__mutmut_orig.__name__ = 'xǁThresholdCounterǁadd'

    def xǁThresholdCounterǁelements__mutmut_orig(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(itertools.repeat, self.iteritems())
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_1(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = None
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_2(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(None, self.iteritems())
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_3(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(itertools.repeat, None)
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_4(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(self.iteritems())
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_5(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(itertools.repeat, )
        return itertools.chain.from_iterable(repeaters)

    def xǁThresholdCounterǁelements__mutmut_6(self):
        """Return an iterator of all the common elements tracked by the
        counter. Yields each key as many times as it has been seen.
        """
        repeaters = itertools.starmap(itertools.repeat, self.iteritems())
        return itertools.chain.from_iterable(None)
    
    xǁThresholdCounterǁelements__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁelements__mutmut_1': xǁThresholdCounterǁelements__mutmut_1, 
        'xǁThresholdCounterǁelements__mutmut_2': xǁThresholdCounterǁelements__mutmut_2, 
        'xǁThresholdCounterǁelements__mutmut_3': xǁThresholdCounterǁelements__mutmut_3, 
        'xǁThresholdCounterǁelements__mutmut_4': xǁThresholdCounterǁelements__mutmut_4, 
        'xǁThresholdCounterǁelements__mutmut_5': xǁThresholdCounterǁelements__mutmut_5, 
        'xǁThresholdCounterǁelements__mutmut_6': xǁThresholdCounterǁelements__mutmut_6
    }
    
    def elements(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁelements__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁelements__mutmut_mutants"), args, kwargs, self)
        return result 
    
    elements.__signature__ = _mutmut_signature(xǁThresholdCounterǁelements__mutmut_orig)
    xǁThresholdCounterǁelements__mutmut_orig.__name__ = 'xǁThresholdCounterǁelements'

    def xǁThresholdCounterǁmost_common__mutmut_orig(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_1(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n and n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_2(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_3(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n < 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_4(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 1:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_5(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = None
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_6(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(None, key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_7(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=None, reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_8(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=None)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_9(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(key=lambda x: x[1], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_10(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_11(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], )
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_12(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: None, reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_13(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[2], reverse=True)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_14(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=False)
        if n is None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_15(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None and n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_16(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is not None or n >= len(ret):
            return ret
        return ret[:n]

    def xǁThresholdCounterǁmost_common__mutmut_17(self, n=None):
        """Get the top *n* keys and counts as tuples. If *n* is omitted,
        returns all the pairs.
        """
        if not n or n <= 0:
            return []
        ret = sorted(self.iteritems(), key=lambda x: x[1], reverse=True)
        if n is None or n > len(ret):
            return ret
        return ret[:n]
    
    xǁThresholdCounterǁmost_common__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁmost_common__mutmut_1': xǁThresholdCounterǁmost_common__mutmut_1, 
        'xǁThresholdCounterǁmost_common__mutmut_2': xǁThresholdCounterǁmost_common__mutmut_2, 
        'xǁThresholdCounterǁmost_common__mutmut_3': xǁThresholdCounterǁmost_common__mutmut_3, 
        'xǁThresholdCounterǁmost_common__mutmut_4': xǁThresholdCounterǁmost_common__mutmut_4, 
        'xǁThresholdCounterǁmost_common__mutmut_5': xǁThresholdCounterǁmost_common__mutmut_5, 
        'xǁThresholdCounterǁmost_common__mutmut_6': xǁThresholdCounterǁmost_common__mutmut_6, 
        'xǁThresholdCounterǁmost_common__mutmut_7': xǁThresholdCounterǁmost_common__mutmut_7, 
        'xǁThresholdCounterǁmost_common__mutmut_8': xǁThresholdCounterǁmost_common__mutmut_8, 
        'xǁThresholdCounterǁmost_common__mutmut_9': xǁThresholdCounterǁmost_common__mutmut_9, 
        'xǁThresholdCounterǁmost_common__mutmut_10': xǁThresholdCounterǁmost_common__mutmut_10, 
        'xǁThresholdCounterǁmost_common__mutmut_11': xǁThresholdCounterǁmost_common__mutmut_11, 
        'xǁThresholdCounterǁmost_common__mutmut_12': xǁThresholdCounterǁmost_common__mutmut_12, 
        'xǁThresholdCounterǁmost_common__mutmut_13': xǁThresholdCounterǁmost_common__mutmut_13, 
        'xǁThresholdCounterǁmost_common__mutmut_14': xǁThresholdCounterǁmost_common__mutmut_14, 
        'xǁThresholdCounterǁmost_common__mutmut_15': xǁThresholdCounterǁmost_common__mutmut_15, 
        'xǁThresholdCounterǁmost_common__mutmut_16': xǁThresholdCounterǁmost_common__mutmut_16, 
        'xǁThresholdCounterǁmost_common__mutmut_17': xǁThresholdCounterǁmost_common__mutmut_17
    }
    
    def most_common(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁmost_common__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁmost_common__mutmut_mutants"), args, kwargs, self)
        return result 
    
    most_common.__signature__ = _mutmut_signature(xǁThresholdCounterǁmost_common__mutmut_orig)
    xǁThresholdCounterǁmost_common__mutmut_orig.__name__ = 'xǁThresholdCounterǁmost_common'

    def xǁThresholdCounterǁget_common_count__mutmut_orig(self):
        """Get the sum of counts for keys exceeding the configured data
        threshold.
        """
        return sum([count for count, _ in self._count_map.values()])

    def xǁThresholdCounterǁget_common_count__mutmut_1(self):
        """Get the sum of counts for keys exceeding the configured data
        threshold.
        """
        return sum(None)
    
    xǁThresholdCounterǁget_common_count__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁget_common_count__mutmut_1': xǁThresholdCounterǁget_common_count__mutmut_1
    }
    
    def get_common_count(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁget_common_count__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁget_common_count__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_common_count.__signature__ = _mutmut_signature(xǁThresholdCounterǁget_common_count__mutmut_orig)
    xǁThresholdCounterǁget_common_count__mutmut_orig.__name__ = 'xǁThresholdCounterǁget_common_count'

    def xǁThresholdCounterǁget_uncommon_count__mutmut_orig(self):
        """Get the sum of counts for keys that were culled because the
        associated counts represented less than the configured
        threshold. The long-tail counts.
        """
        return self.total - self.get_common_count()

    def xǁThresholdCounterǁget_uncommon_count__mutmut_1(self):
        """Get the sum of counts for keys that were culled because the
        associated counts represented less than the configured
        threshold. The long-tail counts.
        """
        return self.total + self.get_common_count()
    
    xǁThresholdCounterǁget_uncommon_count__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁget_uncommon_count__mutmut_1': xǁThresholdCounterǁget_uncommon_count__mutmut_1
    }
    
    def get_uncommon_count(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁget_uncommon_count__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁget_uncommon_count__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_uncommon_count.__signature__ = _mutmut_signature(xǁThresholdCounterǁget_uncommon_count__mutmut_orig)
    xǁThresholdCounterǁget_uncommon_count__mutmut_orig.__name__ = 'xǁThresholdCounterǁget_uncommon_count'

    def xǁThresholdCounterǁget_commonality__mutmut_orig(self):
        """Get a float representation of the effective count accuracy. The
        higher the number, the less uniform the keys being added, and
        the higher accuracy and efficiency of the ThresholdCounter.

        If a stronger measure of data cardinality is required,
        consider using hyperloglog.
        """
        return float(self.get_common_count()) / self.total

    def xǁThresholdCounterǁget_commonality__mutmut_1(self):
        """Get a float representation of the effective count accuracy. The
        higher the number, the less uniform the keys being added, and
        the higher accuracy and efficiency of the ThresholdCounter.

        If a stronger measure of data cardinality is required,
        consider using hyperloglog.
        """
        return float(self.get_common_count()) * self.total

    def xǁThresholdCounterǁget_commonality__mutmut_2(self):
        """Get a float representation of the effective count accuracy. The
        higher the number, the less uniform the keys being added, and
        the higher accuracy and efficiency of the ThresholdCounter.

        If a stronger measure of data cardinality is required,
        consider using hyperloglog.
        """
        return float(None) / self.total
    
    xǁThresholdCounterǁget_commonality__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁget_commonality__mutmut_1': xǁThresholdCounterǁget_commonality__mutmut_1, 
        'xǁThresholdCounterǁget_commonality__mutmut_2': xǁThresholdCounterǁget_commonality__mutmut_2
    }
    
    def get_commonality(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁget_commonality__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁget_commonality__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_commonality.__signature__ = _mutmut_signature(xǁThresholdCounterǁget_commonality__mutmut_orig)
    xǁThresholdCounterǁget_commonality__mutmut_orig.__name__ = 'xǁThresholdCounterǁget_commonality'

    def xǁThresholdCounterǁ__getitem____mutmut_orig(self, key):
        return self._count_map[key][0]

    def xǁThresholdCounterǁ__getitem____mutmut_1(self, key):
        return self._count_map[key][1]
    
    xǁThresholdCounterǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁ__getitem____mutmut_1': xǁThresholdCounterǁ__getitem____mutmut_1
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁThresholdCounterǁ__getitem____mutmut_orig)
    xǁThresholdCounterǁ__getitem____mutmut_orig.__name__ = 'xǁThresholdCounterǁ__getitem__'

    def __len__(self):
        return len(self._count_map)

    def xǁThresholdCounterǁ__contains____mutmut_orig(self, key):
        return key in self._count_map

    def xǁThresholdCounterǁ__contains____mutmut_1(self, key):
        return key not in self._count_map
    
    xǁThresholdCounterǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁ__contains____mutmut_1': xǁThresholdCounterǁ__contains____mutmut_1
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁThresholdCounterǁ__contains____mutmut_orig)
    xǁThresholdCounterǁ__contains____mutmut_orig.__name__ = 'xǁThresholdCounterǁ__contains__'

    def xǁThresholdCounterǁiterkeys__mutmut_orig(self):
        return iter(self._count_map)

    def xǁThresholdCounterǁiterkeys__mutmut_1(self):
        return iter(None)
    
    xǁThresholdCounterǁiterkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁiterkeys__mutmut_1': xǁThresholdCounterǁiterkeys__mutmut_1
    }
    
    def iterkeys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁiterkeys__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁiterkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iterkeys.__signature__ = _mutmut_signature(xǁThresholdCounterǁiterkeys__mutmut_orig)
    xǁThresholdCounterǁiterkeys__mutmut_orig.__name__ = 'xǁThresholdCounterǁiterkeys'

    def xǁThresholdCounterǁkeys__mutmut_orig(self):
        return list(self.iterkeys())

    def xǁThresholdCounterǁkeys__mutmut_1(self):
        return list(None)
    
    xǁThresholdCounterǁkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁkeys__mutmut_1': xǁThresholdCounterǁkeys__mutmut_1
    }
    
    def keys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁkeys__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    keys.__signature__ = _mutmut_signature(xǁThresholdCounterǁkeys__mutmut_orig)
    xǁThresholdCounterǁkeys__mutmut_orig.__name__ = 'xǁThresholdCounterǁkeys'

    def xǁThresholdCounterǁitervalues__mutmut_orig(self):
        count_map = self._count_map
        for k in count_map:
            yield count_map[k][0]

    def xǁThresholdCounterǁitervalues__mutmut_1(self):
        count_map = None
        for k in count_map:
            yield count_map[k][0]

    def xǁThresholdCounterǁitervalues__mutmut_2(self):
        count_map = self._count_map
        for k in count_map:
            yield count_map[k][1]
    
    xǁThresholdCounterǁitervalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁitervalues__mutmut_1': xǁThresholdCounterǁitervalues__mutmut_1, 
        'xǁThresholdCounterǁitervalues__mutmut_2': xǁThresholdCounterǁitervalues__mutmut_2
    }
    
    def itervalues(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁitervalues__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁitervalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    itervalues.__signature__ = _mutmut_signature(xǁThresholdCounterǁitervalues__mutmut_orig)
    xǁThresholdCounterǁitervalues__mutmut_orig.__name__ = 'xǁThresholdCounterǁitervalues'

    def xǁThresholdCounterǁvalues__mutmut_orig(self):
        return list(self.itervalues())

    def xǁThresholdCounterǁvalues__mutmut_1(self):
        return list(None)
    
    xǁThresholdCounterǁvalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁvalues__mutmut_1': xǁThresholdCounterǁvalues__mutmut_1
    }
    
    def values(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁvalues__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁvalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    values.__signature__ = _mutmut_signature(xǁThresholdCounterǁvalues__mutmut_orig)
    xǁThresholdCounterǁvalues__mutmut_orig.__name__ = 'xǁThresholdCounterǁvalues'

    def xǁThresholdCounterǁiteritems__mutmut_orig(self):
        count_map = self._count_map
        for k in count_map:
            yield (k, count_map[k][0])

    def xǁThresholdCounterǁiteritems__mutmut_1(self):
        count_map = None
        for k in count_map:
            yield (k, count_map[k][0])

    def xǁThresholdCounterǁiteritems__mutmut_2(self):
        count_map = self._count_map
        for k in count_map:
            yield (k, count_map[k][1])
    
    xǁThresholdCounterǁiteritems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁiteritems__mutmut_1': xǁThresholdCounterǁiteritems__mutmut_1, 
        'xǁThresholdCounterǁiteritems__mutmut_2': xǁThresholdCounterǁiteritems__mutmut_2
    }
    
    def iteritems(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁiteritems__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁiteritems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iteritems.__signature__ = _mutmut_signature(xǁThresholdCounterǁiteritems__mutmut_orig)
    xǁThresholdCounterǁiteritems__mutmut_orig.__name__ = 'xǁThresholdCounterǁiteritems'

    def xǁThresholdCounterǁitems__mutmut_orig(self):
        return list(self.iteritems())

    def xǁThresholdCounterǁitems__mutmut_1(self):
        return list(None)
    
    xǁThresholdCounterǁitems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁitems__mutmut_1': xǁThresholdCounterǁitems__mutmut_1
    }
    
    def items(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁitems__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁitems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    items.__signature__ = _mutmut_signature(xǁThresholdCounterǁitems__mutmut_orig)
    xǁThresholdCounterǁitems__mutmut_orig.__name__ = 'xǁThresholdCounterǁitems'

    def xǁThresholdCounterǁget__mutmut_orig(self, key, default=0):
        "Get count for *key*, defaulting to 0."
        try:
            return self[key]
        except KeyError:
            return default

    def xǁThresholdCounterǁget__mutmut_1(self, key, default=1):
        "Get count for *key*, defaulting to 0."
        try:
            return self[key]
        except KeyError:
            return default

    def xǁThresholdCounterǁget__mutmut_2(self, key, default=0):
        "XXGet count for *key*, defaulting to 0.XX"
        try:
            return self[key]
        except KeyError:
            return default

    def xǁThresholdCounterǁget__mutmut_3(self, key, default=0):
        "get count for *key*, defaulting to 0."
        try:
            return self[key]
        except KeyError:
            return default

    def xǁThresholdCounterǁget__mutmut_4(self, key, default=0):
        "GET COUNT FOR *KEY*, DEFAULTING TO 0."
        try:
            return self[key]
        except KeyError:
            return default
    
    xǁThresholdCounterǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁget__mutmut_1': xǁThresholdCounterǁget__mutmut_1, 
        'xǁThresholdCounterǁget__mutmut_2': xǁThresholdCounterǁget__mutmut_2, 
        'xǁThresholdCounterǁget__mutmut_3': xǁThresholdCounterǁget__mutmut_3, 
        'xǁThresholdCounterǁget__mutmut_4': xǁThresholdCounterǁget__mutmut_4
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁget__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁThresholdCounterǁget__mutmut_orig)
    xǁThresholdCounterǁget__mutmut_orig.__name__ = 'xǁThresholdCounterǁget'

    def xǁThresholdCounterǁupdate__mutmut_orig(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_1(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_2(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(None):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_3(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(None, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_4(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, None, None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_5(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr('iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_6(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_7(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', )):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_8(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'XXiteritemsXX', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_9(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'ITERITEMS', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_10(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(None):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_11(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(None)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_12(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(None)
        if kwargs:
            self.update(kwargs)

    def xǁThresholdCounterǁupdate__mutmut_13(self, iterable, **kwargs):
        """Like dict.update() but add counts instead of replacing them, used
        to add multiple items in one call.

        Source can be an iterable of keys to add, or a mapping of keys
        to integer counts.
        """
        if iterable is not None:
            if callable(getattr(iterable, 'iteritems', None)):
                for key, count in iterable.iteritems():
                    for i in range(count):
                        self.add(key)
            else:
                for key in iterable:
                    self.add(key)
        if kwargs:
            self.update(None)
    
    xǁThresholdCounterǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁThresholdCounterǁupdate__mutmut_1': xǁThresholdCounterǁupdate__mutmut_1, 
        'xǁThresholdCounterǁupdate__mutmut_2': xǁThresholdCounterǁupdate__mutmut_2, 
        'xǁThresholdCounterǁupdate__mutmut_3': xǁThresholdCounterǁupdate__mutmut_3, 
        'xǁThresholdCounterǁupdate__mutmut_4': xǁThresholdCounterǁupdate__mutmut_4, 
        'xǁThresholdCounterǁupdate__mutmut_5': xǁThresholdCounterǁupdate__mutmut_5, 
        'xǁThresholdCounterǁupdate__mutmut_6': xǁThresholdCounterǁupdate__mutmut_6, 
        'xǁThresholdCounterǁupdate__mutmut_7': xǁThresholdCounterǁupdate__mutmut_7, 
        'xǁThresholdCounterǁupdate__mutmut_8': xǁThresholdCounterǁupdate__mutmut_8, 
        'xǁThresholdCounterǁupdate__mutmut_9': xǁThresholdCounterǁupdate__mutmut_9, 
        'xǁThresholdCounterǁupdate__mutmut_10': xǁThresholdCounterǁupdate__mutmut_10, 
        'xǁThresholdCounterǁupdate__mutmut_11': xǁThresholdCounterǁupdate__mutmut_11, 
        'xǁThresholdCounterǁupdate__mutmut_12': xǁThresholdCounterǁupdate__mutmut_12, 
        'xǁThresholdCounterǁupdate__mutmut_13': xǁThresholdCounterǁupdate__mutmut_13
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁThresholdCounterǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁThresholdCounterǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁThresholdCounterǁupdate__mutmut_orig)
    xǁThresholdCounterǁupdate__mutmut_orig.__name__ = 'xǁThresholdCounterǁupdate'


class MinIDMap:
    """
    Assigns arbitrary weakref-able objects the smallest possible unique
    integer IDs, such that no two objects have the same ID at the same
    time.

    Maps arbitrary hashable objects to IDs.

    Based on https://gist.github.com/kurtbrose/25b48114de216a5e55df
    """
    def xǁMinIDMapǁ__init____mutmut_orig(self):
        self.mapping = weakref.WeakKeyDictionary()
        self.ref_map = {}
        self.free = []
    def xǁMinIDMapǁ__init____mutmut_1(self):
        self.mapping = None
        self.ref_map = {}
        self.free = []
    def xǁMinIDMapǁ__init____mutmut_2(self):
        self.mapping = weakref.WeakKeyDictionary()
        self.ref_map = None
        self.free = []
    def xǁMinIDMapǁ__init____mutmut_3(self):
        self.mapping = weakref.WeakKeyDictionary()
        self.ref_map = {}
        self.free = None
    
    xǁMinIDMapǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁ__init____mutmut_1': xǁMinIDMapǁ__init____mutmut_1, 
        'xǁMinIDMapǁ__init____mutmut_2': xǁMinIDMapǁ__init____mutmut_2, 
        'xǁMinIDMapǁ__init____mutmut_3': xǁMinIDMapǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMinIDMapǁ__init____mutmut_orig)
    xǁMinIDMapǁ__init____mutmut_orig.__name__ = 'xǁMinIDMapǁ__init__'

    def xǁMinIDMapǁget__mutmut_orig(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_1(self, a):
        try:
            return self.mapping[a][1]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_2(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = None
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_3(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(None)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_4(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = None
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_5(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = None
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_6(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(None, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_7(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, None)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_8(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_9(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, )
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_10(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = None
        self.ref_map[ref] = nxt
        return nxt

    def xǁMinIDMapǁget__mutmut_11(self, a):
        try:
            return self.mapping[a][0]  # if object is mapped, return ID
        except KeyError:
            pass

        if self.free:  # if there are any free IDs, use the smallest
            nxt = heapq.heappop(self.free)
        else:  # if there are no free numbers, use the next highest ID
            nxt = len(self.mapping)
        ref = weakref.ref(a, self._clean)
        self.mapping[a] = (nxt, ref)
        self.ref_map[ref] = None
        return nxt
    
    xǁMinIDMapǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁget__mutmut_1': xǁMinIDMapǁget__mutmut_1, 
        'xǁMinIDMapǁget__mutmut_2': xǁMinIDMapǁget__mutmut_2, 
        'xǁMinIDMapǁget__mutmut_3': xǁMinIDMapǁget__mutmut_3, 
        'xǁMinIDMapǁget__mutmut_4': xǁMinIDMapǁget__mutmut_4, 
        'xǁMinIDMapǁget__mutmut_5': xǁMinIDMapǁget__mutmut_5, 
        'xǁMinIDMapǁget__mutmut_6': xǁMinIDMapǁget__mutmut_6, 
        'xǁMinIDMapǁget__mutmut_7': xǁMinIDMapǁget__mutmut_7, 
        'xǁMinIDMapǁget__mutmut_8': xǁMinIDMapǁget__mutmut_8, 
        'xǁMinIDMapǁget__mutmut_9': xǁMinIDMapǁget__mutmut_9, 
        'xǁMinIDMapǁget__mutmut_10': xǁMinIDMapǁget__mutmut_10, 
        'xǁMinIDMapǁget__mutmut_11': xǁMinIDMapǁget__mutmut_11
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁget__mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁMinIDMapǁget__mutmut_orig)
    xǁMinIDMapǁget__mutmut_orig.__name__ = 'xǁMinIDMapǁget'

    def xǁMinIDMapǁdrop__mutmut_orig(self, a):
        freed, ref = self.mapping[a]
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(self.free, freed)

    def xǁMinIDMapǁdrop__mutmut_1(self, a):
        freed, ref = None
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(self.free, freed)

    def xǁMinIDMapǁdrop__mutmut_2(self, a):
        freed, ref = self.mapping[a]
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(None, freed)

    def xǁMinIDMapǁdrop__mutmut_3(self, a):
        freed, ref = self.mapping[a]
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(self.free, None)

    def xǁMinIDMapǁdrop__mutmut_4(self, a):
        freed, ref = self.mapping[a]
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(freed)

    def xǁMinIDMapǁdrop__mutmut_5(self, a):
        freed, ref = self.mapping[a]
        del self.mapping[a]
        del self.ref_map[ref]
        heapq.heappush(self.free, )
    
    xǁMinIDMapǁdrop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁdrop__mutmut_1': xǁMinIDMapǁdrop__mutmut_1, 
        'xǁMinIDMapǁdrop__mutmut_2': xǁMinIDMapǁdrop__mutmut_2, 
        'xǁMinIDMapǁdrop__mutmut_3': xǁMinIDMapǁdrop__mutmut_3, 
        'xǁMinIDMapǁdrop__mutmut_4': xǁMinIDMapǁdrop__mutmut_4, 
        'xǁMinIDMapǁdrop__mutmut_5': xǁMinIDMapǁdrop__mutmut_5
    }
    
    def drop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁdrop__mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁdrop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    drop.__signature__ = _mutmut_signature(xǁMinIDMapǁdrop__mutmut_orig)
    xǁMinIDMapǁdrop__mutmut_orig.__name__ = 'xǁMinIDMapǁdrop'

    def xǁMinIDMapǁ_clean__mutmut_orig(self, ref):
        print(self.ref_map[ref])
        heapq.heappush(self.free, self.ref_map[ref])
        del self.ref_map[ref]

    def xǁMinIDMapǁ_clean__mutmut_1(self, ref):
        print(None)
        heapq.heappush(self.free, self.ref_map[ref])
        del self.ref_map[ref]

    def xǁMinIDMapǁ_clean__mutmut_2(self, ref):
        print(self.ref_map[ref])
        heapq.heappush(None, self.ref_map[ref])
        del self.ref_map[ref]

    def xǁMinIDMapǁ_clean__mutmut_3(self, ref):
        print(self.ref_map[ref])
        heapq.heappush(self.free, None)
        del self.ref_map[ref]

    def xǁMinIDMapǁ_clean__mutmut_4(self, ref):
        print(self.ref_map[ref])
        heapq.heappush(self.ref_map[ref])
        del self.ref_map[ref]

    def xǁMinIDMapǁ_clean__mutmut_5(self, ref):
        print(self.ref_map[ref])
        heapq.heappush(self.free, )
        del self.ref_map[ref]
    
    xǁMinIDMapǁ_clean__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁ_clean__mutmut_1': xǁMinIDMapǁ_clean__mutmut_1, 
        'xǁMinIDMapǁ_clean__mutmut_2': xǁMinIDMapǁ_clean__mutmut_2, 
        'xǁMinIDMapǁ_clean__mutmut_3': xǁMinIDMapǁ_clean__mutmut_3, 
        'xǁMinIDMapǁ_clean__mutmut_4': xǁMinIDMapǁ_clean__mutmut_4, 
        'xǁMinIDMapǁ_clean__mutmut_5': xǁMinIDMapǁ_clean__mutmut_5
    }
    
    def _clean(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁ_clean__mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁ_clean__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _clean.__signature__ = _mutmut_signature(xǁMinIDMapǁ_clean__mutmut_orig)
    xǁMinIDMapǁ_clean__mutmut_orig.__name__ = 'xǁMinIDMapǁ_clean'

    def xǁMinIDMapǁ__contains____mutmut_orig(self, a):
        return a in self.mapping

    def xǁMinIDMapǁ__contains____mutmut_1(self, a):
        return a not in self.mapping
    
    xǁMinIDMapǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁ__contains____mutmut_1': xǁMinIDMapǁ__contains____mutmut_1
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁMinIDMapǁ__contains____mutmut_orig)
    xǁMinIDMapǁ__contains____mutmut_orig.__name__ = 'xǁMinIDMapǁ__contains__'

    def xǁMinIDMapǁ__iter____mutmut_orig(self):
        return iter(self.mapping)

    def xǁMinIDMapǁ__iter____mutmut_1(self):
        return iter(None)
    
    xǁMinIDMapǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁ__iter____mutmut_1': xǁMinIDMapǁ__iter____mutmut_1
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁMinIDMapǁ__iter____mutmut_orig)
    xǁMinIDMapǁ__iter____mutmut_orig.__name__ = 'xǁMinIDMapǁ__iter__'

    def __len__(self):
        return self.mapping.__len__()

    def xǁMinIDMapǁiteritems__mutmut_orig(self):
        return iter((k, self.mapping[k][0]) for k in iter(self.mapping))

    def xǁMinIDMapǁiteritems__mutmut_1(self):
        return iter(None)

    def xǁMinIDMapǁiteritems__mutmut_2(self):
        return iter((k, self.mapping[k][1]) for k in iter(self.mapping))

    def xǁMinIDMapǁiteritems__mutmut_3(self):
        return iter((k, self.mapping[k][0]) for k in iter(None))
    
    xǁMinIDMapǁiteritems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMinIDMapǁiteritems__mutmut_1': xǁMinIDMapǁiteritems__mutmut_1, 
        'xǁMinIDMapǁiteritems__mutmut_2': xǁMinIDMapǁiteritems__mutmut_2, 
        'xǁMinIDMapǁiteritems__mutmut_3': xǁMinIDMapǁiteritems__mutmut_3
    }
    
    def iteritems(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMinIDMapǁiteritems__mutmut_orig"), object.__getattribute__(self, "xǁMinIDMapǁiteritems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iteritems.__signature__ = _mutmut_signature(xǁMinIDMapǁiteritems__mutmut_orig)
    xǁMinIDMapǁiteritems__mutmut_orig.__name__ = 'xǁMinIDMapǁiteritems'


# end cacheutils.py
