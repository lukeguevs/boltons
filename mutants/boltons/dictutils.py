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

"""Python has a very powerful mapping type at its core: the :class:`dict`
type. While versatile and featureful, the :class:`dict` prioritizes
simplicity and performance. As a result, it does not retain the order
of item insertion [1]_, nor does it store multiple values per key. It
is a fast, unordered 1:1 mapping.

The :class:`OrderedMultiDict` contrasts to the built-in :class:`dict`,
as a relatively maximalist, ordered 1:n subtype of
:class:`dict`. Virtually every feature of :class:`dict` has been
retooled to be intuitive in the face of this added
complexity. Additional methods have been added, such as
:class:`collections.Counter`-like functionality.

A prime advantage of the :class:`OrderedMultiDict` (OMD) is its
non-destructive nature. Data can be added to an :class:`OMD` without being
rearranged or overwritten. The property can allow the developer to
work more freely with the data, as well as make more assumptions about
where input data will end up in the output, all without any extra
work.

One great example of this is the :meth:`OMD.inverted()` method, which
returns a new OMD with the values as keys and the keys as values. All
the data and the respective order is still represented in the inverted
form, all from an operation which would be outright wrong and reckless
with a built-in :class:`dict` or :class:`collections.OrderedDict`.

The OMD has been performance tuned to be suitable for a wide range of
usages, including as a basic unordered MultiDict. Special
thanks to `Mark Williams`_ for all his help.

.. [1] As of 2015, `basic dicts on PyPy are ordered
   <http://morepypy.blogspot.com/2015/01/faster-more-memory-efficient-and-more.html>`_,
   and as of December 2017, `basic dicts in CPython 3 are now ordered
   <https://mail.python.org/pipermail/python-dev/2017-December/151283.html>`_, as
   well.
.. _Mark Williams: https://github.com/markrwilliams

"""

from collections.abc import KeysView, ValuesView, ItemsView
from itertools import zip_longest

_MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


__all__ = ['MultiDict', 'OMD', 'OrderedMultiDict', 'OneToOne', 'ManyToMany', 'subdict', 'FrozenDict']
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


class OrderedMultiDict(dict):
    """A MultiDict is a dictionary that can have multiple values per key
    and the OrderedMultiDict (OMD) is a MultiDict that retains
    original insertion order. Common use cases include:

      * handling query strings parsed from URLs
      * inverting a dictionary to create a reverse index (values to keys)
      * stacking data from multiple dictionaries in a non-destructive way

    The OrderedMultiDict constructor is identical to the built-in
    :class:`dict`, and overall the API constitutes an intuitive
    superset of the built-in type:

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd.get('a')
    3
    >>> omd.getlist('a')
    [1, 3]

    Some non-:class:`dict`-like behaviors also make an appearance,
    such as support for :func:`reversed`:

    >>> list(reversed(omd))
    ['b', 'a']

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the most recent value added. ``omd['a']`` refers to ``3``, not
    ``1``.

    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.poplast('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    If you want a safe-to-modify or flat dictionary, use
    :meth:`OrderedMultiDict.todict()`.

    >>> from pprint import pprint as pp  # preserve printed ordering
    >>> omd = OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> pp(omd.todict())
    {'a': 3, 'b': 2}
    >>> pp(omd.todict(multi=True))
    {'a': [1, 3], 'b': [2]}

    With ``multi=False``, items appear with the keys in to original
    insertion order, alongside the most-recently inserted value for
    that key.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

    .. warning::

       ``dict(omd)`` changed behavior `in Python 3.7
       <https://bugs.python.org/issue34320>`_ due to changes made to
       support the transition from :class:`collections.OrderedDict` to
       the built-in dictionary being ordered. Before 3.7, the result
       would be a new dictionary, with values that were lists, similar
       to ``omd.todict(multi=True)`` (but only shallow-copy; the lists
       were direct references to OMD internal structures). From 3.7
       onward, the values became singular, like
       ``omd.todict(multi=False)``. For reliable cross-version
       behavior, just use :meth:`~OrderedMultiDict.todict()`.

    """
    def __new__(cls, *a, **kw):
        ret = super().__new__(cls)
        ret._clear_ll()
        return ret 
    
    def xǁOrderedMultiDictǁ__init____mutmut_orig(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_1(self, *args, **kwargs):
        if len(args) >= 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_2(self, *args, **kwargs):
        if len(args) > 2:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_3(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(None)
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_4(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s' / (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_5(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('XX%s expected at most 1 argument, got %sXX'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_6(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%S EXPECTED AT MOST 1 ARGUMENT, GOT %S'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_7(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(None)
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_8(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[1])
        if kwargs:
            self.update(kwargs)
    
    def xǁOrderedMultiDictǁ__init____mutmut_9(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(None)
    
    xǁOrderedMultiDictǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__init____mutmut_1': xǁOrderedMultiDictǁ__init____mutmut_1, 
        'xǁOrderedMultiDictǁ__init____mutmut_2': xǁOrderedMultiDictǁ__init____mutmut_2, 
        'xǁOrderedMultiDictǁ__init____mutmut_3': xǁOrderedMultiDictǁ__init____mutmut_3, 
        'xǁOrderedMultiDictǁ__init____mutmut_4': xǁOrderedMultiDictǁ__init____mutmut_4, 
        'xǁOrderedMultiDictǁ__init____mutmut_5': xǁOrderedMultiDictǁ__init____mutmut_5, 
        'xǁOrderedMultiDictǁ__init____mutmut_6': xǁOrderedMultiDictǁ__init____mutmut_6, 
        'xǁOrderedMultiDictǁ__init____mutmut_7': xǁOrderedMultiDictǁ__init____mutmut_7, 
        'xǁOrderedMultiDictǁ__init____mutmut_8': xǁOrderedMultiDictǁ__init____mutmut_8, 
        'xǁOrderedMultiDictǁ__init____mutmut_9': xǁOrderedMultiDictǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__init____mutmut_orig)
    xǁOrderedMultiDictǁ__init____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__init__'

    def xǁOrderedMultiDictǁ__getstate____mutmut_orig(self):
        return list(self.iteritems(multi=True))

    def xǁOrderedMultiDictǁ__getstate____mutmut_1(self):
        return list(None)

    def xǁOrderedMultiDictǁ__getstate____mutmut_2(self):
        return list(self.iteritems(multi=None))

    def xǁOrderedMultiDictǁ__getstate____mutmut_3(self):
        return list(self.iteritems(multi=False))
    
    xǁOrderedMultiDictǁ__getstate____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__getstate____mutmut_1': xǁOrderedMultiDictǁ__getstate____mutmut_1, 
        'xǁOrderedMultiDictǁ__getstate____mutmut_2': xǁOrderedMultiDictǁ__getstate____mutmut_2, 
        'xǁOrderedMultiDictǁ__getstate____mutmut_3': xǁOrderedMultiDictǁ__getstate____mutmut_3
    }
    
    def __getstate__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__getstate____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__getstate____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getstate__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__getstate____mutmut_orig)
    xǁOrderedMultiDictǁ__getstate____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__getstate__'

    def xǁOrderedMultiDictǁ__setstate____mutmut_orig(self, state):
        self.clear()
        self.update_extend(state)

    def xǁOrderedMultiDictǁ__setstate____mutmut_1(self, state):
        self.clear()
        self.update_extend(None)
    
    xǁOrderedMultiDictǁ__setstate____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__setstate____mutmut_1': xǁOrderedMultiDictǁ__setstate____mutmut_1
    }
    
    def __setstate__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__setstate____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__setstate____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setstate__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__setstate____mutmut_orig)
    xǁOrderedMultiDictǁ__setstate____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__setstate__'

    def xǁOrderedMultiDictǁ_clear_ll__mutmut_orig(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def xǁOrderedMultiDictǁ_clear_ll__mutmut_1(self):
        try:
            _map = None
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def xǁOrderedMultiDictǁ_clear_ll__mutmut_2(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = None
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def xǁOrderedMultiDictǁ_clear_ll__mutmut_3(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = None
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def xǁOrderedMultiDictǁ_clear_ll__mutmut_4(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = None
    
    xǁOrderedMultiDictǁ_clear_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ_clear_ll__mutmut_1': xǁOrderedMultiDictǁ_clear_ll__mutmut_1, 
        'xǁOrderedMultiDictǁ_clear_ll__mutmut_2': xǁOrderedMultiDictǁ_clear_ll__mutmut_2, 
        'xǁOrderedMultiDictǁ_clear_ll__mutmut_3': xǁOrderedMultiDictǁ_clear_ll__mutmut_3, 
        'xǁOrderedMultiDictǁ_clear_ll__mutmut_4': xǁOrderedMultiDictǁ_clear_ll__mutmut_4
    }
    
    def _clear_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ_clear_ll__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ_clear_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _clear_ll.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ_clear_ll__mutmut_orig)
    xǁOrderedMultiDictǁ_clear_ll__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ_clear_ll'

    def xǁOrderedMultiDictǁ_insert__mutmut_orig(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_1(self, k, v):
        root = None
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_2(self, k, v):
        root = self.root
        cells = None
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_3(self, k, v):
        root = self.root
        cells = self._map.setdefault(None, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_4(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, None)
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_5(self, k, v):
        root = self.root
        cells = self._map.setdefault([])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_6(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, )
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_7(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = None
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_8(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = None
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_9(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = None
        cells.append(cell)

    def xǁOrderedMultiDictǁ_insert__mutmut_10(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(None)
    
    xǁOrderedMultiDictǁ_insert__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ_insert__mutmut_1': xǁOrderedMultiDictǁ_insert__mutmut_1, 
        'xǁOrderedMultiDictǁ_insert__mutmut_2': xǁOrderedMultiDictǁ_insert__mutmut_2, 
        'xǁOrderedMultiDictǁ_insert__mutmut_3': xǁOrderedMultiDictǁ_insert__mutmut_3, 
        'xǁOrderedMultiDictǁ_insert__mutmut_4': xǁOrderedMultiDictǁ_insert__mutmut_4, 
        'xǁOrderedMultiDictǁ_insert__mutmut_5': xǁOrderedMultiDictǁ_insert__mutmut_5, 
        'xǁOrderedMultiDictǁ_insert__mutmut_6': xǁOrderedMultiDictǁ_insert__mutmut_6, 
        'xǁOrderedMultiDictǁ_insert__mutmut_7': xǁOrderedMultiDictǁ_insert__mutmut_7, 
        'xǁOrderedMultiDictǁ_insert__mutmut_8': xǁOrderedMultiDictǁ_insert__mutmut_8, 
        'xǁOrderedMultiDictǁ_insert__mutmut_9': xǁOrderedMultiDictǁ_insert__mutmut_9, 
        'xǁOrderedMultiDictǁ_insert__mutmut_10': xǁOrderedMultiDictǁ_insert__mutmut_10
    }
    
    def _insert(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ_insert__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ_insert__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _insert.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ_insert__mutmut_orig)
    xǁOrderedMultiDictǁ_insert__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ_insert'

    def xǁOrderedMultiDictǁadd__mutmut_orig(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_1(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = None
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_2(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(None, [])
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_3(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, None)
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_4(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault([])
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_5(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, )
        self._insert(k, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_6(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(None, v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_7(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, None)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_8(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(v)
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_9(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, )
        values.append(v)

    def xǁOrderedMultiDictǁadd__mutmut_10(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, v)
        values.append(None)
    
    xǁOrderedMultiDictǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁadd__mutmut_1': xǁOrderedMultiDictǁadd__mutmut_1, 
        'xǁOrderedMultiDictǁadd__mutmut_2': xǁOrderedMultiDictǁadd__mutmut_2, 
        'xǁOrderedMultiDictǁadd__mutmut_3': xǁOrderedMultiDictǁadd__mutmut_3, 
        'xǁOrderedMultiDictǁadd__mutmut_4': xǁOrderedMultiDictǁadd__mutmut_4, 
        'xǁOrderedMultiDictǁadd__mutmut_5': xǁOrderedMultiDictǁadd__mutmut_5, 
        'xǁOrderedMultiDictǁadd__mutmut_6': xǁOrderedMultiDictǁadd__mutmut_6, 
        'xǁOrderedMultiDictǁadd__mutmut_7': xǁOrderedMultiDictǁadd__mutmut_7, 
        'xǁOrderedMultiDictǁadd__mutmut_8': xǁOrderedMultiDictǁadd__mutmut_8, 
        'xǁOrderedMultiDictǁadd__mutmut_9': xǁOrderedMultiDictǁadd__mutmut_9, 
        'xǁOrderedMultiDictǁadd__mutmut_10': xǁOrderedMultiDictǁadd__mutmut_10
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁadd__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁadd__mutmut_orig)
    xǁOrderedMultiDictǁadd__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁadd'

    def xǁOrderedMultiDictǁaddlist__mutmut_orig(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_1(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_2(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = None
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_3(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = None
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_4(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(None, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_5(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, None)
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_6(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault([])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_7(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, )
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_8(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(None, subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_9(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, None)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_10(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(subv)
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_11(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, )
        values.extend(v)

    def xǁOrderedMultiDictǁaddlist__mutmut_12(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(None)
    
    xǁOrderedMultiDictǁaddlist__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁaddlist__mutmut_1': xǁOrderedMultiDictǁaddlist__mutmut_1, 
        'xǁOrderedMultiDictǁaddlist__mutmut_2': xǁOrderedMultiDictǁaddlist__mutmut_2, 
        'xǁOrderedMultiDictǁaddlist__mutmut_3': xǁOrderedMultiDictǁaddlist__mutmut_3, 
        'xǁOrderedMultiDictǁaddlist__mutmut_4': xǁOrderedMultiDictǁaddlist__mutmut_4, 
        'xǁOrderedMultiDictǁaddlist__mutmut_5': xǁOrderedMultiDictǁaddlist__mutmut_5, 
        'xǁOrderedMultiDictǁaddlist__mutmut_6': xǁOrderedMultiDictǁaddlist__mutmut_6, 
        'xǁOrderedMultiDictǁaddlist__mutmut_7': xǁOrderedMultiDictǁaddlist__mutmut_7, 
        'xǁOrderedMultiDictǁaddlist__mutmut_8': xǁOrderedMultiDictǁaddlist__mutmut_8, 
        'xǁOrderedMultiDictǁaddlist__mutmut_9': xǁOrderedMultiDictǁaddlist__mutmut_9, 
        'xǁOrderedMultiDictǁaddlist__mutmut_10': xǁOrderedMultiDictǁaddlist__mutmut_10, 
        'xǁOrderedMultiDictǁaddlist__mutmut_11': xǁOrderedMultiDictǁaddlist__mutmut_11, 
        'xǁOrderedMultiDictǁaddlist__mutmut_12': xǁOrderedMultiDictǁaddlist__mutmut_12
    }
    
    def addlist(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁaddlist__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁaddlist__mutmut_mutants"), args, kwargs, self)
        return result 
    
    addlist.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁaddlist__mutmut_orig)
    xǁOrderedMultiDictǁaddlist__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁaddlist'

    def xǁOrderedMultiDictǁget__mutmut_orig(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, [default])[-1]

    def xǁOrderedMultiDictǁget__mutmut_1(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(None, [default])[-1]

    def xǁOrderedMultiDictǁget__mutmut_2(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, None)[-1]

    def xǁOrderedMultiDictǁget__mutmut_3(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get([default])[-1]

    def xǁOrderedMultiDictǁget__mutmut_4(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, )[-1]

    def xǁOrderedMultiDictǁget__mutmut_5(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, [default])[+1]

    def xǁOrderedMultiDictǁget__mutmut_6(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, [default])[-2]
    
    xǁOrderedMultiDictǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁget__mutmut_1': xǁOrderedMultiDictǁget__mutmut_1, 
        'xǁOrderedMultiDictǁget__mutmut_2': xǁOrderedMultiDictǁget__mutmut_2, 
        'xǁOrderedMultiDictǁget__mutmut_3': xǁOrderedMultiDictǁget__mutmut_3, 
        'xǁOrderedMultiDictǁget__mutmut_4': xǁOrderedMultiDictǁget__mutmut_4, 
        'xǁOrderedMultiDictǁget__mutmut_5': xǁOrderedMultiDictǁget__mutmut_5, 
        'xǁOrderedMultiDictǁget__mutmut_6': xǁOrderedMultiDictǁget__mutmut_6
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁget__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁget__mutmut_orig)
    xǁOrderedMultiDictǁget__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁget'

    def xǁOrderedMultiDictǁgetlist__mutmut_orig(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super().__getitem__(k)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def xǁOrderedMultiDictǁgetlist__mutmut_1(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super().__getitem__(None)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def xǁOrderedMultiDictǁgetlist__mutmut_2(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super().__getitem__(k)[:]
        except KeyError:
            if default is not _MISSING:
                return []
            return default
    
    xǁOrderedMultiDictǁgetlist__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁgetlist__mutmut_1': xǁOrderedMultiDictǁgetlist__mutmut_1, 
        'xǁOrderedMultiDictǁgetlist__mutmut_2': xǁOrderedMultiDictǁgetlist__mutmut_2
    }
    
    def getlist(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁgetlist__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁgetlist__mutmut_mutants"), args, kwargs, self)
        return result 
    
    getlist.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁgetlist__mutmut_orig)
    xǁOrderedMultiDictǁgetlist__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁgetlist'

    def xǁOrderedMultiDictǁclear__mutmut_orig(self):
        "Empty the dictionary."
        super().clear()
        self._clear_ll()

    def xǁOrderedMultiDictǁclear__mutmut_1(self):
        "XXEmpty the dictionary.XX"
        super().clear()
        self._clear_ll()

    def xǁOrderedMultiDictǁclear__mutmut_2(self):
        "empty the dictionary."
        super().clear()
        self._clear_ll()

    def xǁOrderedMultiDictǁclear__mutmut_3(self):
        "EMPTY THE DICTIONARY."
        super().clear()
        self._clear_ll()
    
    xǁOrderedMultiDictǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁclear__mutmut_1': xǁOrderedMultiDictǁclear__mutmut_1, 
        'xǁOrderedMultiDictǁclear__mutmut_2': xǁOrderedMultiDictǁclear__mutmut_2, 
        'xǁOrderedMultiDictǁclear__mutmut_3': xǁOrderedMultiDictǁclear__mutmut_3
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁclear__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁclear__mutmut_orig)
    xǁOrderedMultiDictǁclear__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁclear'

    def xǁOrderedMultiDictǁsetdefault__mutmut_orig(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(k):
            self[k] = None if default is _MISSING else default
        return self[k]

    def xǁOrderedMultiDictǁsetdefault__mutmut_1(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if super().__contains__(k):
            self[k] = None if default is _MISSING else default
        return self[k]

    def xǁOrderedMultiDictǁsetdefault__mutmut_2(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(None):
            self[k] = None if default is _MISSING else default
        return self[k]

    def xǁOrderedMultiDictǁsetdefault__mutmut_3(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(k):
            self[k] = None
        return self[k]

    def xǁOrderedMultiDictǁsetdefault__mutmut_4(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(k):
            self[k] = None if default is not _MISSING else default
        return self[k]
    
    xǁOrderedMultiDictǁsetdefault__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁsetdefault__mutmut_1': xǁOrderedMultiDictǁsetdefault__mutmut_1, 
        'xǁOrderedMultiDictǁsetdefault__mutmut_2': xǁOrderedMultiDictǁsetdefault__mutmut_2, 
        'xǁOrderedMultiDictǁsetdefault__mutmut_3': xǁOrderedMultiDictǁsetdefault__mutmut_3, 
        'xǁOrderedMultiDictǁsetdefault__mutmut_4': xǁOrderedMultiDictǁsetdefault__mutmut_4
    }
    
    def setdefault(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁsetdefault__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁsetdefault__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setdefault.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁsetdefault__mutmut_orig)
    xǁOrderedMultiDictǁsetdefault__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁsetdefault'

    def xǁOrderedMultiDictǁcopy__mutmut_orig(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    def xǁOrderedMultiDictǁcopy__mutmut_1(self):
        "XXReturn a shallow copy of the dictionary.XX"
        return self.__class__(self.iteritems(multi=True))

    def xǁOrderedMultiDictǁcopy__mutmut_2(self):
        "return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    def xǁOrderedMultiDictǁcopy__mutmut_3(self):
        "RETURN A SHALLOW COPY OF THE DICTIONARY."
        return self.__class__(self.iteritems(multi=True))

    def xǁOrderedMultiDictǁcopy__mutmut_4(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(None)

    def xǁOrderedMultiDictǁcopy__mutmut_5(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=None))

    def xǁOrderedMultiDictǁcopy__mutmut_6(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=False))
    
    xǁOrderedMultiDictǁcopy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁcopy__mutmut_1': xǁOrderedMultiDictǁcopy__mutmut_1, 
        'xǁOrderedMultiDictǁcopy__mutmut_2': xǁOrderedMultiDictǁcopy__mutmut_2, 
        'xǁOrderedMultiDictǁcopy__mutmut_3': xǁOrderedMultiDictǁcopy__mutmut_3, 
        'xǁOrderedMultiDictǁcopy__mutmut_4': xǁOrderedMultiDictǁcopy__mutmut_4, 
        'xǁOrderedMultiDictǁcopy__mutmut_5': xǁOrderedMultiDictǁcopy__mutmut_5, 
        'xǁOrderedMultiDictǁcopy__mutmut_6': xǁOrderedMultiDictǁcopy__mutmut_6
    }
    
    def copy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁcopy__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁcopy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    copy.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁcopy__mutmut_orig)
    xǁOrderedMultiDictǁcopy__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁcopy'

    @classmethod
    def fromkeys(cls, keys, default=None):
        """Create a dictionary from a list of keys, with all the values
        set to *default*, or ``None`` if *default* is not set.
        """
        return cls([(k, default) for k in keys])

    def xǁOrderedMultiDictǁupdate__mutmut_orig(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_1(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is not self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_2(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = None
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_3(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k not in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_4(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=None):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_5(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=False):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_6(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(None, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_7(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, None)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_8(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_9(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, )
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_10(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(None):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_11(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(None, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_12(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, None, None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_13(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr('keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_14(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_15(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', )):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_16(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'XXkeysXX', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_17(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'KEYS', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_18(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = None
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_19(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = None
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_20(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = None
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_21(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen or k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_22(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_23(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k not in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_24(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(None)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_25(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(None, v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_26(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, None)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_27(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(v)
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_28(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, )
        for k in F:
            self[k] = F[k]
        return

    def xǁOrderedMultiDictǁupdate__mutmut_29(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = None
        return
    
    xǁOrderedMultiDictǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁupdate__mutmut_1': xǁOrderedMultiDictǁupdate__mutmut_1, 
        'xǁOrderedMultiDictǁupdate__mutmut_2': xǁOrderedMultiDictǁupdate__mutmut_2, 
        'xǁOrderedMultiDictǁupdate__mutmut_3': xǁOrderedMultiDictǁupdate__mutmut_3, 
        'xǁOrderedMultiDictǁupdate__mutmut_4': xǁOrderedMultiDictǁupdate__mutmut_4, 
        'xǁOrderedMultiDictǁupdate__mutmut_5': xǁOrderedMultiDictǁupdate__mutmut_5, 
        'xǁOrderedMultiDictǁupdate__mutmut_6': xǁOrderedMultiDictǁupdate__mutmut_6, 
        'xǁOrderedMultiDictǁupdate__mutmut_7': xǁOrderedMultiDictǁupdate__mutmut_7, 
        'xǁOrderedMultiDictǁupdate__mutmut_8': xǁOrderedMultiDictǁupdate__mutmut_8, 
        'xǁOrderedMultiDictǁupdate__mutmut_9': xǁOrderedMultiDictǁupdate__mutmut_9, 
        'xǁOrderedMultiDictǁupdate__mutmut_10': xǁOrderedMultiDictǁupdate__mutmut_10, 
        'xǁOrderedMultiDictǁupdate__mutmut_11': xǁOrderedMultiDictǁupdate__mutmut_11, 
        'xǁOrderedMultiDictǁupdate__mutmut_12': xǁOrderedMultiDictǁupdate__mutmut_12, 
        'xǁOrderedMultiDictǁupdate__mutmut_13': xǁOrderedMultiDictǁupdate__mutmut_13, 
        'xǁOrderedMultiDictǁupdate__mutmut_14': xǁOrderedMultiDictǁupdate__mutmut_14, 
        'xǁOrderedMultiDictǁupdate__mutmut_15': xǁOrderedMultiDictǁupdate__mutmut_15, 
        'xǁOrderedMultiDictǁupdate__mutmut_16': xǁOrderedMultiDictǁupdate__mutmut_16, 
        'xǁOrderedMultiDictǁupdate__mutmut_17': xǁOrderedMultiDictǁupdate__mutmut_17, 
        'xǁOrderedMultiDictǁupdate__mutmut_18': xǁOrderedMultiDictǁupdate__mutmut_18, 
        'xǁOrderedMultiDictǁupdate__mutmut_19': xǁOrderedMultiDictǁupdate__mutmut_19, 
        'xǁOrderedMultiDictǁupdate__mutmut_20': xǁOrderedMultiDictǁupdate__mutmut_20, 
        'xǁOrderedMultiDictǁupdate__mutmut_21': xǁOrderedMultiDictǁupdate__mutmut_21, 
        'xǁOrderedMultiDictǁupdate__mutmut_22': xǁOrderedMultiDictǁupdate__mutmut_22, 
        'xǁOrderedMultiDictǁupdate__mutmut_23': xǁOrderedMultiDictǁupdate__mutmut_23, 
        'xǁOrderedMultiDictǁupdate__mutmut_24': xǁOrderedMultiDictǁupdate__mutmut_24, 
        'xǁOrderedMultiDictǁupdate__mutmut_25': xǁOrderedMultiDictǁupdate__mutmut_25, 
        'xǁOrderedMultiDictǁupdate__mutmut_26': xǁOrderedMultiDictǁupdate__mutmut_26, 
        'xǁOrderedMultiDictǁupdate__mutmut_27': xǁOrderedMultiDictǁupdate__mutmut_27, 
        'xǁOrderedMultiDictǁupdate__mutmut_28': xǁOrderedMultiDictǁupdate__mutmut_28, 
        'xǁOrderedMultiDictǁupdate__mutmut_29': xǁOrderedMultiDictǁupdate__mutmut_29
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁupdate__mutmut_orig)
    xǁOrderedMultiDictǁupdate__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁupdate'

    def xǁOrderedMultiDictǁupdate_extend__mutmut_orig(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_1(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is not self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_2(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = None
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_3(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(None)
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_4(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = None
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_5(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=None)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_6(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=False)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_7(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(None, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_8(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, None):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_9(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr('keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_10(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, ):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_11(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'XXkeysXX'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_12(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'KEYS'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_13(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = None
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_14(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = None

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_15(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = None
        for k, v in iterator:
            self_add(k, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_16(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(None, v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_17(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, None)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_18(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(v)

    def xǁOrderedMultiDictǁupdate_extend__mutmut_19(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, )
    
    xǁOrderedMultiDictǁupdate_extend__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁupdate_extend__mutmut_1': xǁOrderedMultiDictǁupdate_extend__mutmut_1, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_2': xǁOrderedMultiDictǁupdate_extend__mutmut_2, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_3': xǁOrderedMultiDictǁupdate_extend__mutmut_3, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_4': xǁOrderedMultiDictǁupdate_extend__mutmut_4, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_5': xǁOrderedMultiDictǁupdate_extend__mutmut_5, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_6': xǁOrderedMultiDictǁupdate_extend__mutmut_6, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_7': xǁOrderedMultiDictǁupdate_extend__mutmut_7, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_8': xǁOrderedMultiDictǁupdate_extend__mutmut_8, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_9': xǁOrderedMultiDictǁupdate_extend__mutmut_9, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_10': xǁOrderedMultiDictǁupdate_extend__mutmut_10, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_11': xǁOrderedMultiDictǁupdate_extend__mutmut_11, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_12': xǁOrderedMultiDictǁupdate_extend__mutmut_12, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_13': xǁOrderedMultiDictǁupdate_extend__mutmut_13, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_14': xǁOrderedMultiDictǁupdate_extend__mutmut_14, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_15': xǁOrderedMultiDictǁupdate_extend__mutmut_15, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_16': xǁOrderedMultiDictǁupdate_extend__mutmut_16, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_17': xǁOrderedMultiDictǁupdate_extend__mutmut_17, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_18': xǁOrderedMultiDictǁupdate_extend__mutmut_18, 
        'xǁOrderedMultiDictǁupdate_extend__mutmut_19': xǁOrderedMultiDictǁupdate_extend__mutmut_19
    }
    
    def update_extend(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁupdate_extend__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁupdate_extend__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update_extend.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁupdate_extend__mutmut_orig)
    xǁOrderedMultiDictǁupdate_extend__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁupdate_extend'

    def xǁOrderedMultiDictǁ__setitem____mutmut_orig(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_1(self, k, v):
        if super().__contains__(None):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_2(self, k, v):
        if super().__contains__(k):
            self._remove_all(None)
        self._insert(k, v)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_3(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(None, v)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_4(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, None)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_5(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(v)
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_6(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, )
        super().__setitem__(k, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_7(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(None, [v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_8(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, None)

    def xǁOrderedMultiDictǁ__setitem____mutmut_9(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__([v])

    def xǁOrderedMultiDictǁ__setitem____mutmut_10(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, )
    
    xǁOrderedMultiDictǁ__setitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__setitem____mutmut_1': xǁOrderedMultiDictǁ__setitem____mutmut_1, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_2': xǁOrderedMultiDictǁ__setitem____mutmut_2, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_3': xǁOrderedMultiDictǁ__setitem____mutmut_3, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_4': xǁOrderedMultiDictǁ__setitem____mutmut_4, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_5': xǁOrderedMultiDictǁ__setitem____mutmut_5, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_6': xǁOrderedMultiDictǁ__setitem____mutmut_6, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_7': xǁOrderedMultiDictǁ__setitem____mutmut_7, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_8': xǁOrderedMultiDictǁ__setitem____mutmut_8, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_9': xǁOrderedMultiDictǁ__setitem____mutmut_9, 
        'xǁOrderedMultiDictǁ__setitem____mutmut_10': xǁOrderedMultiDictǁ__setitem____mutmut_10
    }
    
    def __setitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__setitem____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__setitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setitem__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__setitem____mutmut_orig)
    xǁOrderedMultiDictǁ__setitem____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__setitem__'

    def xǁOrderedMultiDictǁ__getitem____mutmut_orig(self, k):
        return super().__getitem__(k)[-1]

    def xǁOrderedMultiDictǁ__getitem____mutmut_1(self, k):
        return super().__getitem__(None)[-1]

    def xǁOrderedMultiDictǁ__getitem____mutmut_2(self, k):
        return super().__getitem__(k)[+1]

    def xǁOrderedMultiDictǁ__getitem____mutmut_3(self, k):
        return super().__getitem__(k)[-2]
    
    xǁOrderedMultiDictǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__getitem____mutmut_1': xǁOrderedMultiDictǁ__getitem____mutmut_1, 
        'xǁOrderedMultiDictǁ__getitem____mutmut_2': xǁOrderedMultiDictǁ__getitem____mutmut_2, 
        'xǁOrderedMultiDictǁ__getitem____mutmut_3': xǁOrderedMultiDictǁ__getitem____mutmut_3
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__getitem____mutmut_orig)
    xǁOrderedMultiDictǁ__getitem____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__getitem__'

    def xǁOrderedMultiDictǁ__delitem____mutmut_orig(self, k):
        super().__delitem__(k)
        self._remove_all(k)

    def xǁOrderedMultiDictǁ__delitem____mutmut_1(self, k):
        super().__delitem__(None)
        self._remove_all(k)

    def xǁOrderedMultiDictǁ__delitem____mutmut_2(self, k):
        super().__delitem__(k)
        self._remove_all(None)
    
    xǁOrderedMultiDictǁ__delitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__delitem____mutmut_1': xǁOrderedMultiDictǁ__delitem____mutmut_1, 
        'xǁOrderedMultiDictǁ__delitem____mutmut_2': xǁOrderedMultiDictǁ__delitem____mutmut_2
    }
    
    def __delitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__delitem____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__delitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delitem__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__delitem____mutmut_orig)
    xǁOrderedMultiDictǁ__delitem____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__delitem__'

    def xǁOrderedMultiDictǁ__eq____mutmut_orig(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_1(self, other):
        if self is not other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_2(self, other):
        if self is other:
            return False
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_3(self, other):
        if self is other:
            return True
        try:
            if len(other) == len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_4(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return True
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_5(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return True
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_6(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = None
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_7(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=None)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_8(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=False)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_9(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = None
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_10(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=None)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_11(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=False)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_12(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = None
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_13(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(None, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_14(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, None, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_15(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=None)
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_16(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_17(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_18(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, )
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_19(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk and selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_20(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk == otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_21(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv == otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_22(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return True
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_23(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if (next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_24(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING or next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_25(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(None, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_26(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, None) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_27(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(_MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_28(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, ) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_29(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is not _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_30(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(None, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_31(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, None) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_32(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(_MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_33(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, ) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_34(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is not _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_35(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return True
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_36(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return False
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_37(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(None, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_38(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, None):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_39(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr('keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_40(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, ):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_41(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'XXkeysXX'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_42(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'KEYS'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_43(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] != self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_44(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return True
            return True
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_45(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return False
        return False

    def xǁOrderedMultiDictǁ__eq____mutmut_46(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return True
    
    xǁOrderedMultiDictǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__eq____mutmut_1': xǁOrderedMultiDictǁ__eq____mutmut_1, 
        'xǁOrderedMultiDictǁ__eq____mutmut_2': xǁOrderedMultiDictǁ__eq____mutmut_2, 
        'xǁOrderedMultiDictǁ__eq____mutmut_3': xǁOrderedMultiDictǁ__eq____mutmut_3, 
        'xǁOrderedMultiDictǁ__eq____mutmut_4': xǁOrderedMultiDictǁ__eq____mutmut_4, 
        'xǁOrderedMultiDictǁ__eq____mutmut_5': xǁOrderedMultiDictǁ__eq____mutmut_5, 
        'xǁOrderedMultiDictǁ__eq____mutmut_6': xǁOrderedMultiDictǁ__eq____mutmut_6, 
        'xǁOrderedMultiDictǁ__eq____mutmut_7': xǁOrderedMultiDictǁ__eq____mutmut_7, 
        'xǁOrderedMultiDictǁ__eq____mutmut_8': xǁOrderedMultiDictǁ__eq____mutmut_8, 
        'xǁOrderedMultiDictǁ__eq____mutmut_9': xǁOrderedMultiDictǁ__eq____mutmut_9, 
        'xǁOrderedMultiDictǁ__eq____mutmut_10': xǁOrderedMultiDictǁ__eq____mutmut_10, 
        'xǁOrderedMultiDictǁ__eq____mutmut_11': xǁOrderedMultiDictǁ__eq____mutmut_11, 
        'xǁOrderedMultiDictǁ__eq____mutmut_12': xǁOrderedMultiDictǁ__eq____mutmut_12, 
        'xǁOrderedMultiDictǁ__eq____mutmut_13': xǁOrderedMultiDictǁ__eq____mutmut_13, 
        'xǁOrderedMultiDictǁ__eq____mutmut_14': xǁOrderedMultiDictǁ__eq____mutmut_14, 
        'xǁOrderedMultiDictǁ__eq____mutmut_15': xǁOrderedMultiDictǁ__eq____mutmut_15, 
        'xǁOrderedMultiDictǁ__eq____mutmut_16': xǁOrderedMultiDictǁ__eq____mutmut_16, 
        'xǁOrderedMultiDictǁ__eq____mutmut_17': xǁOrderedMultiDictǁ__eq____mutmut_17, 
        'xǁOrderedMultiDictǁ__eq____mutmut_18': xǁOrderedMultiDictǁ__eq____mutmut_18, 
        'xǁOrderedMultiDictǁ__eq____mutmut_19': xǁOrderedMultiDictǁ__eq____mutmut_19, 
        'xǁOrderedMultiDictǁ__eq____mutmut_20': xǁOrderedMultiDictǁ__eq____mutmut_20, 
        'xǁOrderedMultiDictǁ__eq____mutmut_21': xǁOrderedMultiDictǁ__eq____mutmut_21, 
        'xǁOrderedMultiDictǁ__eq____mutmut_22': xǁOrderedMultiDictǁ__eq____mutmut_22, 
        'xǁOrderedMultiDictǁ__eq____mutmut_23': xǁOrderedMultiDictǁ__eq____mutmut_23, 
        'xǁOrderedMultiDictǁ__eq____mutmut_24': xǁOrderedMultiDictǁ__eq____mutmut_24, 
        'xǁOrderedMultiDictǁ__eq____mutmut_25': xǁOrderedMultiDictǁ__eq____mutmut_25, 
        'xǁOrderedMultiDictǁ__eq____mutmut_26': xǁOrderedMultiDictǁ__eq____mutmut_26, 
        'xǁOrderedMultiDictǁ__eq____mutmut_27': xǁOrderedMultiDictǁ__eq____mutmut_27, 
        'xǁOrderedMultiDictǁ__eq____mutmut_28': xǁOrderedMultiDictǁ__eq____mutmut_28, 
        'xǁOrderedMultiDictǁ__eq____mutmut_29': xǁOrderedMultiDictǁ__eq____mutmut_29, 
        'xǁOrderedMultiDictǁ__eq____mutmut_30': xǁOrderedMultiDictǁ__eq____mutmut_30, 
        'xǁOrderedMultiDictǁ__eq____mutmut_31': xǁOrderedMultiDictǁ__eq____mutmut_31, 
        'xǁOrderedMultiDictǁ__eq____mutmut_32': xǁOrderedMultiDictǁ__eq____mutmut_32, 
        'xǁOrderedMultiDictǁ__eq____mutmut_33': xǁOrderedMultiDictǁ__eq____mutmut_33, 
        'xǁOrderedMultiDictǁ__eq____mutmut_34': xǁOrderedMultiDictǁ__eq____mutmut_34, 
        'xǁOrderedMultiDictǁ__eq____mutmut_35': xǁOrderedMultiDictǁ__eq____mutmut_35, 
        'xǁOrderedMultiDictǁ__eq____mutmut_36': xǁOrderedMultiDictǁ__eq____mutmut_36, 
        'xǁOrderedMultiDictǁ__eq____mutmut_37': xǁOrderedMultiDictǁ__eq____mutmut_37, 
        'xǁOrderedMultiDictǁ__eq____mutmut_38': xǁOrderedMultiDictǁ__eq____mutmut_38, 
        'xǁOrderedMultiDictǁ__eq____mutmut_39': xǁOrderedMultiDictǁ__eq____mutmut_39, 
        'xǁOrderedMultiDictǁ__eq____mutmut_40': xǁOrderedMultiDictǁ__eq____mutmut_40, 
        'xǁOrderedMultiDictǁ__eq____mutmut_41': xǁOrderedMultiDictǁ__eq____mutmut_41, 
        'xǁOrderedMultiDictǁ__eq____mutmut_42': xǁOrderedMultiDictǁ__eq____mutmut_42, 
        'xǁOrderedMultiDictǁ__eq____mutmut_43': xǁOrderedMultiDictǁ__eq____mutmut_43, 
        'xǁOrderedMultiDictǁ__eq____mutmut_44': xǁOrderedMultiDictǁ__eq____mutmut_44, 
        'xǁOrderedMultiDictǁ__eq____mutmut_45': xǁOrderedMultiDictǁ__eq____mutmut_45, 
        'xǁOrderedMultiDictǁ__eq____mutmut_46': xǁOrderedMultiDictǁ__eq____mutmut_46
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__eq____mutmut_orig)
    xǁOrderedMultiDictǁ__eq____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__eq__'

    def xǁOrderedMultiDictǁ__ne____mutmut_orig(self, other):
        return not (self == other)

    def xǁOrderedMultiDictǁ__ne____mutmut_1(self, other):
        return (self == other)

    def xǁOrderedMultiDictǁ__ne____mutmut_2(self, other):
        return not (self != other)
    
    xǁOrderedMultiDictǁ__ne____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__ne____mutmut_1': xǁOrderedMultiDictǁ__ne____mutmut_1, 
        'xǁOrderedMultiDictǁ__ne____mutmut_2': xǁOrderedMultiDictǁ__ne____mutmut_2
    }
    
    def __ne__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__ne____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__ne____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ne__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__ne____mutmut_orig)
    xǁOrderedMultiDictǁ__ne____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__ne__'

    def xǁOrderedMultiDictǁ__ior____mutmut_orig(self, other):
        self.update(other)
        return self

    def xǁOrderedMultiDictǁ__ior____mutmut_1(self, other):
        self.update(None)
        return self
    
    xǁOrderedMultiDictǁ__ior____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__ior____mutmut_1': xǁOrderedMultiDictǁ__ior____mutmut_1
    }
    
    def __ior__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__ior____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__ior____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __ior__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__ior____mutmut_orig)
    xǁOrderedMultiDictǁ__ior____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__ior__'

    def xǁOrderedMultiDictǁpop__mutmut_orig(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def xǁOrderedMultiDictǁpop__mutmut_1(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(None)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def xǁOrderedMultiDictǁpop__mutmut_2(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[+1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def xǁOrderedMultiDictǁpop__mutmut_3(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-2]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def xǁOrderedMultiDictǁpop__mutmut_4(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is not _MISSING:
                raise KeyError(k)
        return default

    def xǁOrderedMultiDictǁpop__mutmut_5(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(None)
        return default
    
    xǁOrderedMultiDictǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁpop__mutmut_1': xǁOrderedMultiDictǁpop__mutmut_1, 
        'xǁOrderedMultiDictǁpop__mutmut_2': xǁOrderedMultiDictǁpop__mutmut_2, 
        'xǁOrderedMultiDictǁpop__mutmut_3': xǁOrderedMultiDictǁpop__mutmut_3, 
        'xǁOrderedMultiDictǁpop__mutmut_4': xǁOrderedMultiDictǁpop__mutmut_4, 
        'xǁOrderedMultiDictǁpop__mutmut_5': xǁOrderedMultiDictǁpop__mutmut_5
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁpop__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁpop__mutmut_orig)
    xǁOrderedMultiDictǁpop__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁpop'

    def xǁOrderedMultiDictǁpopall__mutmut_orig(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_1(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = None
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_2(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(None):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_3(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(None)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_4(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is not _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_5(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(None)
        return super_self.pop(k, default)

    def xǁOrderedMultiDictǁpopall__mutmut_6(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(None, default)

    def xǁOrderedMultiDictǁpopall__mutmut_7(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, None)

    def xǁOrderedMultiDictǁpopall__mutmut_8(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(default)

    def xǁOrderedMultiDictǁpopall__mutmut_9(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, )
    
    xǁOrderedMultiDictǁpopall__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁpopall__mutmut_1': xǁOrderedMultiDictǁpopall__mutmut_1, 
        'xǁOrderedMultiDictǁpopall__mutmut_2': xǁOrderedMultiDictǁpopall__mutmut_2, 
        'xǁOrderedMultiDictǁpopall__mutmut_3': xǁOrderedMultiDictǁpopall__mutmut_3, 
        'xǁOrderedMultiDictǁpopall__mutmut_4': xǁOrderedMultiDictǁpopall__mutmut_4, 
        'xǁOrderedMultiDictǁpopall__mutmut_5': xǁOrderedMultiDictǁpopall__mutmut_5, 
        'xǁOrderedMultiDictǁpopall__mutmut_6': xǁOrderedMultiDictǁpopall__mutmut_6, 
        'xǁOrderedMultiDictǁpopall__mutmut_7': xǁOrderedMultiDictǁpopall__mutmut_7, 
        'xǁOrderedMultiDictǁpopall__mutmut_8': xǁOrderedMultiDictǁpopall__mutmut_8, 
        'xǁOrderedMultiDictǁpopall__mutmut_9': xǁOrderedMultiDictǁpopall__mutmut_9
    }
    
    def popall(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁpopall__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁpopall__mutmut_mutants"), args, kwargs, self)
        return result 
    
    popall.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁpopall__mutmut_orig)
    xǁOrderedMultiDictǁpopall__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁpopall'

    def xǁOrderedMultiDictǁpoplast__mutmut_orig(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_1(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is not _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_2(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = None
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_3(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is not _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_4(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError(None)
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_5(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' / type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_6(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('XXempty %rXX' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_7(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('EMPTY %R' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_8(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(None))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_9(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(None)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_10(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is not _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_11(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(None)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_12(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = None
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_13(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(None)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_14(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = None
        if not values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_15(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if values:
            super().__delitem__(k)
        return v

    def xǁOrderedMultiDictǁpoplast__mutmut_16(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(None)
        return v
    
    xǁOrderedMultiDictǁpoplast__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁpoplast__mutmut_1': xǁOrderedMultiDictǁpoplast__mutmut_1, 
        'xǁOrderedMultiDictǁpoplast__mutmut_2': xǁOrderedMultiDictǁpoplast__mutmut_2, 
        'xǁOrderedMultiDictǁpoplast__mutmut_3': xǁOrderedMultiDictǁpoplast__mutmut_3, 
        'xǁOrderedMultiDictǁpoplast__mutmut_4': xǁOrderedMultiDictǁpoplast__mutmut_4, 
        'xǁOrderedMultiDictǁpoplast__mutmut_5': xǁOrderedMultiDictǁpoplast__mutmut_5, 
        'xǁOrderedMultiDictǁpoplast__mutmut_6': xǁOrderedMultiDictǁpoplast__mutmut_6, 
        'xǁOrderedMultiDictǁpoplast__mutmut_7': xǁOrderedMultiDictǁpoplast__mutmut_7, 
        'xǁOrderedMultiDictǁpoplast__mutmut_8': xǁOrderedMultiDictǁpoplast__mutmut_8, 
        'xǁOrderedMultiDictǁpoplast__mutmut_9': xǁOrderedMultiDictǁpoplast__mutmut_9, 
        'xǁOrderedMultiDictǁpoplast__mutmut_10': xǁOrderedMultiDictǁpoplast__mutmut_10, 
        'xǁOrderedMultiDictǁpoplast__mutmut_11': xǁOrderedMultiDictǁpoplast__mutmut_11, 
        'xǁOrderedMultiDictǁpoplast__mutmut_12': xǁOrderedMultiDictǁpoplast__mutmut_12, 
        'xǁOrderedMultiDictǁpoplast__mutmut_13': xǁOrderedMultiDictǁpoplast__mutmut_13, 
        'xǁOrderedMultiDictǁpoplast__mutmut_14': xǁOrderedMultiDictǁpoplast__mutmut_14, 
        'xǁOrderedMultiDictǁpoplast__mutmut_15': xǁOrderedMultiDictǁpoplast__mutmut_15, 
        'xǁOrderedMultiDictǁpoplast__mutmut_16': xǁOrderedMultiDictǁpoplast__mutmut_16
    }
    
    def poplast(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁpoplast__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁpoplast__mutmut_mutants"), args, kwargs, self)
        return result 
    
    poplast.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁpoplast__mutmut_orig)
    xǁOrderedMultiDictǁpoplast__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁpoplast'

    def xǁOrderedMultiDictǁ_remove__mutmut_orig(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def xǁOrderedMultiDictǁ_remove__mutmut_1(self, k):
        values = None
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def xǁOrderedMultiDictǁ_remove__mutmut_2(self, k):
        values = self._map[k]
        cell = None
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def xǁOrderedMultiDictǁ_remove__mutmut_3(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = None
        if not values:
            del self._map[k]

    def xǁOrderedMultiDictǁ_remove__mutmut_4(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if values:
            del self._map[k]
    
    xǁOrderedMultiDictǁ_remove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ_remove__mutmut_1': xǁOrderedMultiDictǁ_remove__mutmut_1, 
        'xǁOrderedMultiDictǁ_remove__mutmut_2': xǁOrderedMultiDictǁ_remove__mutmut_2, 
        'xǁOrderedMultiDictǁ_remove__mutmut_3': xǁOrderedMultiDictǁ_remove__mutmut_3, 
        'xǁOrderedMultiDictǁ_remove__mutmut_4': xǁOrderedMultiDictǁ_remove__mutmut_4
    }
    
    def _remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ_remove__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ_remove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ_remove__mutmut_orig)
    xǁOrderedMultiDictǁ_remove__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ_remove'

    def xǁOrderedMultiDictǁ_remove_all__mutmut_orig(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def xǁOrderedMultiDictǁ_remove_all__mutmut_1(self, k):
        values = None
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def xǁOrderedMultiDictǁ_remove_all__mutmut_2(self, k):
        values = self._map[k]
        while values:
            cell = None
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def xǁOrderedMultiDictǁ_remove_all__mutmut_3(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = None
        del self._map[k]
    
    xǁOrderedMultiDictǁ_remove_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ_remove_all__mutmut_1': xǁOrderedMultiDictǁ_remove_all__mutmut_1, 
        'xǁOrderedMultiDictǁ_remove_all__mutmut_2': xǁOrderedMultiDictǁ_remove_all__mutmut_2, 
        'xǁOrderedMultiDictǁ_remove_all__mutmut_3': xǁOrderedMultiDictǁ_remove_all__mutmut_3
    }
    
    def _remove_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ_remove_all__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ_remove_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove_all.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ_remove_all__mutmut_orig)
    xǁOrderedMultiDictǁ_remove_all__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ_remove_all'

    def xǁOrderedMultiDictǁiteritems__mutmut_orig(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def xǁOrderedMultiDictǁiteritems__mutmut_1(self, multi=True):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def xǁOrderedMultiDictǁiteritems__mutmut_2(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = None
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def xǁOrderedMultiDictǁiteritems__mutmut_3(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = None
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def xǁOrderedMultiDictǁiteritems__mutmut_4(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def xǁOrderedMultiDictǁiteritems__mutmut_5(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = None
        else:
            for key in self.iterkeys():
                yield key, self[key]
    
    xǁOrderedMultiDictǁiteritems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁiteritems__mutmut_1': xǁOrderedMultiDictǁiteritems__mutmut_1, 
        'xǁOrderedMultiDictǁiteritems__mutmut_2': xǁOrderedMultiDictǁiteritems__mutmut_2, 
        'xǁOrderedMultiDictǁiteritems__mutmut_3': xǁOrderedMultiDictǁiteritems__mutmut_3, 
        'xǁOrderedMultiDictǁiteritems__mutmut_4': xǁOrderedMultiDictǁiteritems__mutmut_4, 
        'xǁOrderedMultiDictǁiteritems__mutmut_5': xǁOrderedMultiDictǁiteritems__mutmut_5
    }
    
    def iteritems(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁiteritems__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁiteritems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iteritems.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁiteritems__mutmut_orig)
    xǁOrderedMultiDictǁiteritems__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁiteritems'

    def xǁOrderedMultiDictǁiterkeys__mutmut_orig(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_1(self, multi=True):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_2(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = None
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_3(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = None
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_4(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_5(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = None
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_6(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = None
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_7(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = None
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_8(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_9(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = None
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_10(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_11(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(None)
                    yield k
                curr = curr[NEXT]

    def xǁOrderedMultiDictǁiterkeys__mutmut_12(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = None
    
    xǁOrderedMultiDictǁiterkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁiterkeys__mutmut_1': xǁOrderedMultiDictǁiterkeys__mutmut_1, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_2': xǁOrderedMultiDictǁiterkeys__mutmut_2, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_3': xǁOrderedMultiDictǁiterkeys__mutmut_3, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_4': xǁOrderedMultiDictǁiterkeys__mutmut_4, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_5': xǁOrderedMultiDictǁiterkeys__mutmut_5, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_6': xǁOrderedMultiDictǁiterkeys__mutmut_6, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_7': xǁOrderedMultiDictǁiterkeys__mutmut_7, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_8': xǁOrderedMultiDictǁiterkeys__mutmut_8, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_9': xǁOrderedMultiDictǁiterkeys__mutmut_9, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_10': xǁOrderedMultiDictǁiterkeys__mutmut_10, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_11': xǁOrderedMultiDictǁiterkeys__mutmut_11, 
        'xǁOrderedMultiDictǁiterkeys__mutmut_12': xǁOrderedMultiDictǁiterkeys__mutmut_12
    }
    
    def iterkeys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁiterkeys__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁiterkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iterkeys.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁiterkeys__mutmut_orig)
    xǁOrderedMultiDictǁiterkeys__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁiterkeys'

    def xǁOrderedMultiDictǁitervalues__mutmut_orig(self, multi=False):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def xǁOrderedMultiDictǁitervalues__mutmut_1(self, multi=True):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def xǁOrderedMultiDictǁitervalues__mutmut_2(self, multi=False):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=None):
            yield v
    
    xǁOrderedMultiDictǁitervalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁitervalues__mutmut_1': xǁOrderedMultiDictǁitervalues__mutmut_1, 
        'xǁOrderedMultiDictǁitervalues__mutmut_2': xǁOrderedMultiDictǁitervalues__mutmut_2
    }
    
    def itervalues(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁitervalues__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁitervalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    itervalues.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁitervalues__mutmut_orig)
    xǁOrderedMultiDictǁitervalues__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁitervalues'

    def xǁOrderedMultiDictǁtodict__mutmut_orig(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return {k: self.getlist(k) for k in self}
        return {k: self[k] for k in self}

    def xǁOrderedMultiDictǁtodict__mutmut_1(self, multi=True):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return {k: self.getlist(k) for k in self}
        return {k: self[k] for k in self}

    def xǁOrderedMultiDictǁtodict__mutmut_2(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return {k: self.getlist(None) for k in self}
        return {k: self[k] for k in self}
    
    xǁOrderedMultiDictǁtodict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁtodict__mutmut_1': xǁOrderedMultiDictǁtodict__mutmut_1, 
        'xǁOrderedMultiDictǁtodict__mutmut_2': xǁOrderedMultiDictǁtodict__mutmut_2
    }
    
    def todict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁtodict__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁtodict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    todict.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁtodict__mutmut_orig)
    xǁOrderedMultiDictǁtodict__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁtodict'

    def xǁOrderedMultiDictǁsorted__mutmut_orig(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_1(self, key=None, reverse=True):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_2(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = None
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_3(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(None)

    def xǁOrderedMultiDictǁsorted__mutmut_4(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(None, key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_5(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=None, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_6(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=None))

    def xǁOrderedMultiDictǁsorted__mutmut_7(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_8(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_9(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, ))

    def xǁOrderedMultiDictǁsorted__mutmut_10(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=None), key=key, reverse=reverse))

    def xǁOrderedMultiDictǁsorted__mutmut_11(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=False), key=key, reverse=reverse))
    
    xǁOrderedMultiDictǁsorted__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁsorted__mutmut_1': xǁOrderedMultiDictǁsorted__mutmut_1, 
        'xǁOrderedMultiDictǁsorted__mutmut_2': xǁOrderedMultiDictǁsorted__mutmut_2, 
        'xǁOrderedMultiDictǁsorted__mutmut_3': xǁOrderedMultiDictǁsorted__mutmut_3, 
        'xǁOrderedMultiDictǁsorted__mutmut_4': xǁOrderedMultiDictǁsorted__mutmut_4, 
        'xǁOrderedMultiDictǁsorted__mutmut_5': xǁOrderedMultiDictǁsorted__mutmut_5, 
        'xǁOrderedMultiDictǁsorted__mutmut_6': xǁOrderedMultiDictǁsorted__mutmut_6, 
        'xǁOrderedMultiDictǁsorted__mutmut_7': xǁOrderedMultiDictǁsorted__mutmut_7, 
        'xǁOrderedMultiDictǁsorted__mutmut_8': xǁOrderedMultiDictǁsorted__mutmut_8, 
        'xǁOrderedMultiDictǁsorted__mutmut_9': xǁOrderedMultiDictǁsorted__mutmut_9, 
        'xǁOrderedMultiDictǁsorted__mutmut_10': xǁOrderedMultiDictǁsorted__mutmut_10, 
        'xǁOrderedMultiDictǁsorted__mutmut_11': xǁOrderedMultiDictǁsorted__mutmut_11
    }
    
    def sorted(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁsorted__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁsorted__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sorted.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁsorted__mutmut_orig)
    xǁOrderedMultiDictǁsorted__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁsorted'

    def xǁOrderedMultiDictǁsortedvalues__mutmut_orig(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_1(self, key=None, reverse=True):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_2(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = None
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_3(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = None
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_4(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = None
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_5(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(None, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_6(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=None, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_7(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=None)
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_8(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_9(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_10(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, )
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_11(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=reverse)
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_12(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = None
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_13(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=None):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_14(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=False):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_15(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(None, sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_16(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, None)
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_17(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(sorted_val_map[k].pop())
        return ret

    def xǁOrderedMultiDictǁsortedvalues__mutmut_18(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, )
        return ret
    
    xǁOrderedMultiDictǁsortedvalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁsortedvalues__mutmut_1': xǁOrderedMultiDictǁsortedvalues__mutmut_1, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_2': xǁOrderedMultiDictǁsortedvalues__mutmut_2, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_3': xǁOrderedMultiDictǁsortedvalues__mutmut_3, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_4': xǁOrderedMultiDictǁsortedvalues__mutmut_4, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_5': xǁOrderedMultiDictǁsortedvalues__mutmut_5, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_6': xǁOrderedMultiDictǁsortedvalues__mutmut_6, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_7': xǁOrderedMultiDictǁsortedvalues__mutmut_7, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_8': xǁOrderedMultiDictǁsortedvalues__mutmut_8, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_9': xǁOrderedMultiDictǁsortedvalues__mutmut_9, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_10': xǁOrderedMultiDictǁsortedvalues__mutmut_10, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_11': xǁOrderedMultiDictǁsortedvalues__mutmut_11, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_12': xǁOrderedMultiDictǁsortedvalues__mutmut_12, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_13': xǁOrderedMultiDictǁsortedvalues__mutmut_13, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_14': xǁOrderedMultiDictǁsortedvalues__mutmut_14, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_15': xǁOrderedMultiDictǁsortedvalues__mutmut_15, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_16': xǁOrderedMultiDictǁsortedvalues__mutmut_16, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_17': xǁOrderedMultiDictǁsortedvalues__mutmut_17, 
        'xǁOrderedMultiDictǁsortedvalues__mutmut_18': xǁOrderedMultiDictǁsortedvalues__mutmut_18
    }
    
    def sortedvalues(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁsortedvalues__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁsortedvalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sortedvalues.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁsortedvalues__mutmut_orig)
    xǁOrderedMultiDictǁsortedvalues__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁsortedvalues'

    def xǁOrderedMultiDictǁinverted__mutmut_orig(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=True))

    def xǁOrderedMultiDictǁinverted__mutmut_1(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__(None)

    def xǁOrderedMultiDictǁinverted__mutmut_2(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=None))

    def xǁOrderedMultiDictǁinverted__mutmut_3(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=False))
    
    xǁOrderedMultiDictǁinverted__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁinverted__mutmut_1': xǁOrderedMultiDictǁinverted__mutmut_1, 
        'xǁOrderedMultiDictǁinverted__mutmut_2': xǁOrderedMultiDictǁinverted__mutmut_2, 
        'xǁOrderedMultiDictǁinverted__mutmut_3': xǁOrderedMultiDictǁinverted__mutmut_3
    }
    
    def inverted(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁinverted__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁinverted__mutmut_mutants"), args, kwargs, self)
        return result 
    
    inverted.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁinverted__mutmut_orig)
    xǁOrderedMultiDictǁinverted__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁinverted'

    def xǁOrderedMultiDictǁcounts__mutmut_orig(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super().__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def xǁOrderedMultiDictǁcounts__mutmut_1(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = None
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def xǁOrderedMultiDictǁcounts__mutmut_2(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super().__getitem__
        return self.__class__(None)
    
    xǁOrderedMultiDictǁcounts__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁcounts__mutmut_1': xǁOrderedMultiDictǁcounts__mutmut_1, 
        'xǁOrderedMultiDictǁcounts__mutmut_2': xǁOrderedMultiDictǁcounts__mutmut_2
    }
    
    def counts(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁcounts__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁcounts__mutmut_mutants"), args, kwargs, self)
        return result 
    
    counts.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁcounts__mutmut_orig)
    xǁOrderedMultiDictǁcounts__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁcounts'

    def xǁOrderedMultiDictǁkeys__mutmut_orig(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def xǁOrderedMultiDictǁkeys__mutmut_1(self, multi=True):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def xǁOrderedMultiDictǁkeys__mutmut_2(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(None)

    def xǁOrderedMultiDictǁkeys__mutmut_3(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=None))
    
    xǁOrderedMultiDictǁkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁkeys__mutmut_1': xǁOrderedMultiDictǁkeys__mutmut_1, 
        'xǁOrderedMultiDictǁkeys__mutmut_2': xǁOrderedMultiDictǁkeys__mutmut_2, 
        'xǁOrderedMultiDictǁkeys__mutmut_3': xǁOrderedMultiDictǁkeys__mutmut_3
    }
    
    def keys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁkeys__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    keys.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁkeys__mutmut_orig)
    xǁOrderedMultiDictǁkeys__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁkeys'

    def xǁOrderedMultiDictǁvalues__mutmut_orig(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def xǁOrderedMultiDictǁvalues__mutmut_1(self, multi=True):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def xǁOrderedMultiDictǁvalues__mutmut_2(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(None)

    def xǁOrderedMultiDictǁvalues__mutmut_3(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=None))
    
    xǁOrderedMultiDictǁvalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁvalues__mutmut_1': xǁOrderedMultiDictǁvalues__mutmut_1, 
        'xǁOrderedMultiDictǁvalues__mutmut_2': xǁOrderedMultiDictǁvalues__mutmut_2, 
        'xǁOrderedMultiDictǁvalues__mutmut_3': xǁOrderedMultiDictǁvalues__mutmut_3
    }
    
    def values(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁvalues__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁvalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    values.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁvalues__mutmut_orig)
    xǁOrderedMultiDictǁvalues__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁvalues'

    def xǁOrderedMultiDictǁitems__mutmut_orig(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=multi))

    def xǁOrderedMultiDictǁitems__mutmut_1(self, multi=True):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=multi))

    def xǁOrderedMultiDictǁitems__mutmut_2(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(None)

    def xǁOrderedMultiDictǁitems__mutmut_3(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=None))
    
    xǁOrderedMultiDictǁitems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁitems__mutmut_1': xǁOrderedMultiDictǁitems__mutmut_1, 
        'xǁOrderedMultiDictǁitems__mutmut_2': xǁOrderedMultiDictǁitems__mutmut_2, 
        'xǁOrderedMultiDictǁitems__mutmut_3': xǁOrderedMultiDictǁitems__mutmut_3
    }
    
    def items(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁitems__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁitems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    items.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁitems__mutmut_orig)
    xǁOrderedMultiDictǁitems__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁitems'

    def __iter__(self):
        return self.iterkeys()

    def xǁOrderedMultiDictǁ__reversed____mutmut_orig(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_1(self):
        root = None
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_2(self):
        root = self.root
        curr = None
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_3(self):
        root = self.root
        curr = root[PREV]
        lengths = None
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_4(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = None
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_5(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = None
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_6(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_7(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = None
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_8(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = None
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_9(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(None)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_10(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(None, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_11(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, None) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_12(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_13(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, ) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_14(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 2) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_15(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) != len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_16(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] = 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_17(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] -= 1
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_18(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 2
            curr = curr[PREV]

    def xǁOrderedMultiDictǁ__reversed____mutmut_19(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = None
    
    xǁOrderedMultiDictǁ__reversed____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__reversed____mutmut_1': xǁOrderedMultiDictǁ__reversed____mutmut_1, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_2': xǁOrderedMultiDictǁ__reversed____mutmut_2, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_3': xǁOrderedMultiDictǁ__reversed____mutmut_3, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_4': xǁOrderedMultiDictǁ__reversed____mutmut_4, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_5': xǁOrderedMultiDictǁ__reversed____mutmut_5, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_6': xǁOrderedMultiDictǁ__reversed____mutmut_6, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_7': xǁOrderedMultiDictǁ__reversed____mutmut_7, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_8': xǁOrderedMultiDictǁ__reversed____mutmut_8, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_9': xǁOrderedMultiDictǁ__reversed____mutmut_9, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_10': xǁOrderedMultiDictǁ__reversed____mutmut_10, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_11': xǁOrderedMultiDictǁ__reversed____mutmut_11, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_12': xǁOrderedMultiDictǁ__reversed____mutmut_12, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_13': xǁOrderedMultiDictǁ__reversed____mutmut_13, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_14': xǁOrderedMultiDictǁ__reversed____mutmut_14, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_15': xǁOrderedMultiDictǁ__reversed____mutmut_15, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_16': xǁOrderedMultiDictǁ__reversed____mutmut_16, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_17': xǁOrderedMultiDictǁ__reversed____mutmut_17, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_18': xǁOrderedMultiDictǁ__reversed____mutmut_18, 
        'xǁOrderedMultiDictǁ__reversed____mutmut_19': xǁOrderedMultiDictǁ__reversed____mutmut_19
    }
    
    def __reversed__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__reversed____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__reversed____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __reversed__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__reversed____mutmut_orig)
    xǁOrderedMultiDictǁ__reversed____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__reversed__'

    def xǁOrderedMultiDictǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_1(self):
        cn = None
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        kvs = None
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        kvs = ', '.join(None)
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_4(self):
        cn = self.__class__.__name__
        kvs = 'XX, XX'.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_5(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr(None) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_6(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=None)])
        return f'{cn}([{kvs}])'

    def xǁOrderedMultiDictǁ__repr____mutmut_7(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=False)])
        return f'{cn}([{kvs}])'
    
    xǁOrderedMultiDictǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁ__repr____mutmut_1': xǁOrderedMultiDictǁ__repr____mutmut_1, 
        'xǁOrderedMultiDictǁ__repr____mutmut_2': xǁOrderedMultiDictǁ__repr____mutmut_2, 
        'xǁOrderedMultiDictǁ__repr____mutmut_3': xǁOrderedMultiDictǁ__repr____mutmut_3, 
        'xǁOrderedMultiDictǁ__repr____mutmut_4': xǁOrderedMultiDictǁ__repr____mutmut_4, 
        'xǁOrderedMultiDictǁ__repr____mutmut_5': xǁOrderedMultiDictǁ__repr____mutmut_5, 
        'xǁOrderedMultiDictǁ__repr____mutmut_6': xǁOrderedMultiDictǁ__repr____mutmut_6, 
        'xǁOrderedMultiDictǁ__repr____mutmut_7': xǁOrderedMultiDictǁ__repr____mutmut_7
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁ__repr____mutmut_orig)
    xǁOrderedMultiDictǁ__repr____mutmut_orig.__name__ = 'xǁOrderedMultiDictǁ__repr__'

    def xǁOrderedMultiDictǁviewkeys__mutmut_orig(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(self)

    def xǁOrderedMultiDictǁviewkeys__mutmut_1(self):
        "XXOMD.viewkeys() -> a set-like object providing a view on OMD's keysXX"
        return KeysView(self)

    def xǁOrderedMultiDictǁviewkeys__mutmut_2(self):
        "omd.viewkeys() -> a set-like object providing a view on omd's keys"
        return KeysView(self)

    def xǁOrderedMultiDictǁviewkeys__mutmut_3(self):
        "OMD.VIEWKEYS() -> A SET-LIKE OBJECT PROVIDING A VIEW ON OMD'S KEYS"
        return KeysView(self)

    def xǁOrderedMultiDictǁviewkeys__mutmut_4(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(None)
    
    xǁOrderedMultiDictǁviewkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁviewkeys__mutmut_1': xǁOrderedMultiDictǁviewkeys__mutmut_1, 
        'xǁOrderedMultiDictǁviewkeys__mutmut_2': xǁOrderedMultiDictǁviewkeys__mutmut_2, 
        'xǁOrderedMultiDictǁviewkeys__mutmut_3': xǁOrderedMultiDictǁviewkeys__mutmut_3, 
        'xǁOrderedMultiDictǁviewkeys__mutmut_4': xǁOrderedMultiDictǁviewkeys__mutmut_4
    }
    
    def viewkeys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁviewkeys__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁviewkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    viewkeys.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁviewkeys__mutmut_orig)
    xǁOrderedMultiDictǁviewkeys__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁviewkeys'

    def xǁOrderedMultiDictǁviewvalues__mutmut_orig(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(self)

    def xǁOrderedMultiDictǁviewvalues__mutmut_1(self):
        "XXOMD.viewvalues() -> an object providing a view on OMD's valuesXX"
        return ValuesView(self)

    def xǁOrderedMultiDictǁviewvalues__mutmut_2(self):
        "omd.viewvalues() -> an object providing a view on omd's values"
        return ValuesView(self)

    def xǁOrderedMultiDictǁviewvalues__mutmut_3(self):
        "OMD.VIEWVALUES() -> AN OBJECT PROVIDING A VIEW ON OMD'S VALUES"
        return ValuesView(self)

    def xǁOrderedMultiDictǁviewvalues__mutmut_4(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(None)
    
    xǁOrderedMultiDictǁviewvalues__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁviewvalues__mutmut_1': xǁOrderedMultiDictǁviewvalues__mutmut_1, 
        'xǁOrderedMultiDictǁviewvalues__mutmut_2': xǁOrderedMultiDictǁviewvalues__mutmut_2, 
        'xǁOrderedMultiDictǁviewvalues__mutmut_3': xǁOrderedMultiDictǁviewvalues__mutmut_3, 
        'xǁOrderedMultiDictǁviewvalues__mutmut_4': xǁOrderedMultiDictǁviewvalues__mutmut_4
    }
    
    def viewvalues(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁviewvalues__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁviewvalues__mutmut_mutants"), args, kwargs, self)
        return result 
    
    viewvalues.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁviewvalues__mutmut_orig)
    xǁOrderedMultiDictǁviewvalues__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁviewvalues'

    def xǁOrderedMultiDictǁviewitems__mutmut_orig(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(self)

    def xǁOrderedMultiDictǁviewitems__mutmut_1(self):
        "XXOMD.viewitems() -> a set-like object providing a view on OMD's itemsXX"
        return ItemsView(self)

    def xǁOrderedMultiDictǁviewitems__mutmut_2(self):
        "omd.viewitems() -> a set-like object providing a view on omd's items"
        return ItemsView(self)

    def xǁOrderedMultiDictǁviewitems__mutmut_3(self):
        "OMD.VIEWITEMS() -> A SET-LIKE OBJECT PROVIDING A VIEW ON OMD'S ITEMS"
        return ItemsView(self)

    def xǁOrderedMultiDictǁviewitems__mutmut_4(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(None)
    
    xǁOrderedMultiDictǁviewitems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOrderedMultiDictǁviewitems__mutmut_1': xǁOrderedMultiDictǁviewitems__mutmut_1, 
        'xǁOrderedMultiDictǁviewitems__mutmut_2': xǁOrderedMultiDictǁviewitems__mutmut_2, 
        'xǁOrderedMultiDictǁviewitems__mutmut_3': xǁOrderedMultiDictǁviewitems__mutmut_3, 
        'xǁOrderedMultiDictǁviewitems__mutmut_4': xǁOrderedMultiDictǁviewitems__mutmut_4
    }
    
    def viewitems(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOrderedMultiDictǁviewitems__mutmut_orig"), object.__getattribute__(self, "xǁOrderedMultiDictǁviewitems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    viewitems.__signature__ = _mutmut_signature(xǁOrderedMultiDictǁviewitems__mutmut_orig)
    xǁOrderedMultiDictǁviewitems__mutmut_orig.__name__ = 'xǁOrderedMultiDictǁviewitems'


# A couple of convenient aliases
OMD = OrderedMultiDict
MultiDict = OrderedMultiDict


class FastIterOrderedMultiDict(OrderedMultiDict):
    """An OrderedMultiDict backed by a skip list.  Iteration over keys
    is faster and uses constant memory but adding duplicate key-value
    pairs is slower. Brainchild of Mark Williams.
    """
    def xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_orig(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]
    def xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_1(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = None
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]
    def xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_2(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = None
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]
    def xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_3(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = None
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]
    def xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_4(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = None
    
    xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_1': xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_2': xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_3': xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_4': xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_4
    }
    
    def _clear_ll(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _clear_ll.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_orig)
    xǁFastIterOrderedMultiDictǁ_clear_ll__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁ_clear_ll'

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_orig(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_1(self, k, v):
        root = None
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_2(self, k, v):
        root = self.root
        empty = None
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_3(self, k, v):
        root = self.root
        empty = []
        cells = None
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_4(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(None, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_5(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, None)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_6(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_7(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, )
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_8(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = None

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_9(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is not empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_10(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = None
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_11(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is not root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_12(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = None
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_13(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = None
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_14(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(None)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_15(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = None
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_16(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_17(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = None
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_18(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = None
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_19(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = None
            cells.append(cell)

    def xǁFastIterOrderedMultiDictǁ_insert__mutmut_20(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if (last[SPREV][SNEXT] is not last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(None)
    
    xǁFastIterOrderedMultiDictǁ_insert__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁ_insert__mutmut_1': xǁFastIterOrderedMultiDictǁ_insert__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_2': xǁFastIterOrderedMultiDictǁ_insert__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_3': xǁFastIterOrderedMultiDictǁ_insert__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_4': xǁFastIterOrderedMultiDictǁ_insert__mutmut_4, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_5': xǁFastIterOrderedMultiDictǁ_insert__mutmut_5, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_6': xǁFastIterOrderedMultiDictǁ_insert__mutmut_6, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_7': xǁFastIterOrderedMultiDictǁ_insert__mutmut_7, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_8': xǁFastIterOrderedMultiDictǁ_insert__mutmut_8, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_9': xǁFastIterOrderedMultiDictǁ_insert__mutmut_9, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_10': xǁFastIterOrderedMultiDictǁ_insert__mutmut_10, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_11': xǁFastIterOrderedMultiDictǁ_insert__mutmut_11, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_12': xǁFastIterOrderedMultiDictǁ_insert__mutmut_12, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_13': xǁFastIterOrderedMultiDictǁ_insert__mutmut_13, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_14': xǁFastIterOrderedMultiDictǁ_insert__mutmut_14, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_15': xǁFastIterOrderedMultiDictǁ_insert__mutmut_15, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_16': xǁFastIterOrderedMultiDictǁ_insert__mutmut_16, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_17': xǁFastIterOrderedMultiDictǁ_insert__mutmut_17, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_18': xǁFastIterOrderedMultiDictǁ_insert__mutmut_18, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_19': xǁFastIterOrderedMultiDictǁ_insert__mutmut_19, 
        'xǁFastIterOrderedMultiDictǁ_insert__mutmut_20': xǁFastIterOrderedMultiDictǁ_insert__mutmut_20
    }
    
    def _insert(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_insert__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_insert__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _insert.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁ_insert__mutmut_orig)
    xǁFastIterOrderedMultiDictǁ_insert__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁ_insert'

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_orig(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_1(self, k):
        cells = None
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_2(self, k):
        cells = self._map[k]
        cell = None
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_3(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_4(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = None

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_5(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is not cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_6(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = None
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_7(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is not cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_8(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = None

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def xǁFastIterOrderedMultiDictǁ_remove__mutmut_9(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = None
    
    xǁFastIterOrderedMultiDictǁ_remove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁ_remove__mutmut_1': xǁFastIterOrderedMultiDictǁ_remove__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_2': xǁFastIterOrderedMultiDictǁ_remove__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_3': xǁFastIterOrderedMultiDictǁ_remove__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_4': xǁFastIterOrderedMultiDictǁ_remove__mutmut_4, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_5': xǁFastIterOrderedMultiDictǁ_remove__mutmut_5, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_6': xǁFastIterOrderedMultiDictǁ_remove__mutmut_6, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_7': xǁFastIterOrderedMultiDictǁ_remove__mutmut_7, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_8': xǁFastIterOrderedMultiDictǁ_remove__mutmut_8, 
        'xǁFastIterOrderedMultiDictǁ_remove__mutmut_9': xǁFastIterOrderedMultiDictǁ_remove__mutmut_9
    }
    
    def _remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_remove__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_remove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁ_remove__mutmut_orig)
    xǁFastIterOrderedMultiDictǁ_remove__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁ_remove'

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_orig(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_1(self, k):
        cells = None
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_2(self, k):
        cells = self._map.pop(None)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_3(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = None
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_4(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is not cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_5(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = None
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_6(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is not cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_7(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = None

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_8(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = None
        cell[PREV][SNEXT] = cell[SNEXT]

    def xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_9(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = None
    
    xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_1': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_2': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_3': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_4': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_4, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_5': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_5, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_6': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_6, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_7': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_7, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_8': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_8, 
        'xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_9': xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_9
    }
    
    def _remove_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _remove_all.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_orig)
    xǁFastIterOrderedMultiDictǁ_remove_all__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁ_remove_all'

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_orig(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_1(self, multi=True):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_2(self, multi=False):
        next_link = None
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_3(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = None
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_4(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = None
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_5(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiteritems__mutmut_6(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = None
    
    xǁFastIterOrderedMultiDictǁiteritems__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁiteritems__mutmut_1': xǁFastIterOrderedMultiDictǁiteritems__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁiteritems__mutmut_2': xǁFastIterOrderedMultiDictǁiteritems__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁiteritems__mutmut_3': xǁFastIterOrderedMultiDictǁiteritems__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁiteritems__mutmut_4': xǁFastIterOrderedMultiDictǁiteritems__mutmut_4, 
        'xǁFastIterOrderedMultiDictǁiteritems__mutmut_5': xǁFastIterOrderedMultiDictǁiteritems__mutmut_5, 
        'xǁFastIterOrderedMultiDictǁiteritems__mutmut_6': xǁFastIterOrderedMultiDictǁiteritems__mutmut_6
    }
    
    def iteritems(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁiteritems__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁiteritems__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iteritems.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁiteritems__mutmut_orig)
    xǁFastIterOrderedMultiDictǁiteritems__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁiteritems'

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_orig(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_1(self, multi=True):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_2(self, multi=False):
        next_link = None
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_3(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = None
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_4(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = None
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_5(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is root:
            yield curr[KEY]
            curr = curr[next_link]

    def xǁFastIterOrderedMultiDictǁiterkeys__mutmut_6(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = None
    
    xǁFastIterOrderedMultiDictǁiterkeys__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_1': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_1, 
        'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_2': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_2, 
        'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_3': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_3, 
        'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_4': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_4, 
        'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_5': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_5, 
        'xǁFastIterOrderedMultiDictǁiterkeys__mutmut_6': xǁFastIterOrderedMultiDictǁiterkeys__mutmut_6
    }
    
    def iterkeys(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁiterkeys__mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁiterkeys__mutmut_mutants"), args, kwargs, self)
        return result 
    
    iterkeys.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁiterkeys__mutmut_orig)
    xǁFastIterOrderedMultiDictǁiterkeys__mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁiterkeys'

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_orig(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_1(self):
        root = None
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_2(self):
        root = self.root
        curr = None
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_3(self):
        root = self.root
        curr = root[PREV]
        while curr is root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_4(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_5(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = None
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_6(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is not root:
                    break
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_7(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    return
            yield curr[KEY]
            curr = curr[PREV]

    def xǁFastIterOrderedMultiDictǁ__reversed____mutmut_8(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = None
    
    xǁFastIterOrderedMultiDictǁ__reversed____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_1': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_1, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_2': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_2, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_3': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_3, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_4': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_4, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_5': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_5, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_6': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_6, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_7': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_7, 
        'xǁFastIterOrderedMultiDictǁ__reversed____mutmut_8': xǁFastIterOrderedMultiDictǁ__reversed____mutmut_8
    }
    
    def __reversed__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ__reversed____mutmut_orig"), object.__getattribute__(self, "xǁFastIterOrderedMultiDictǁ__reversed____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __reversed__.__signature__ = _mutmut_signature(xǁFastIterOrderedMultiDictǁ__reversed____mutmut_orig)
    xǁFastIterOrderedMultiDictǁ__reversed____mutmut_orig.__name__ = 'xǁFastIterOrderedMultiDictǁ__reversed__'


_OTO_INV_MARKER = object()
_OTO_UNIQUE_MARKER = object()


class OneToOne(dict):
    """Implements a one-to-one mapping dictionary. In addition to
    inheriting from and behaving exactly like the builtin
    :class:`dict`, all values are automatically added as keys on a
    reverse mapping, available as the `inv` attribute. This
    arrangement keeps key and value namespaces distinct.

    Basic operations are intuitive:

    >>> oto = OneToOne({'a': 1, 'b': 2})
    >>> print(oto['a'])
    1
    >>> print(oto.inv[1])
    a
    >>> len(oto)
    2

    Overwrites happens in both directions:

    >>> oto.inv[1] = 'c'
    >>> print(oto.get('a'))
    None
    >>> len(oto)
    2

    For a very similar project, with even more one-to-one
    functionality, check out `bidict <https://github.com/jab/bidict>`_.
    """
    __slots__ = ('inv',)

    def xǁOneToOneǁ__init____mutmut_orig(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_1(self, *a, **kw):
        raise_on_dupe = None
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_2(self, *a, **kw):
        raise_on_dupe = True
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_3(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[1] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_4(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is not _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_5(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = None
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_6(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[2]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_7(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(None, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_8(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, None)
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_9(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__([(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_10(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, )
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_11(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[1] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_12(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is not _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_13(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = None

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_14(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[2:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_15(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], False

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_16(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(None, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_17(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(*a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_18(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_19(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, )
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_20(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = None

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_21(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(None, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_22(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, None)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_23(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_24(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, )

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_25(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) != len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_26(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_27(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(None)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_28(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(None, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_29(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, None)
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_30(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update([(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_31(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, )
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_32(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = None
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_33(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(None)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_34(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(None, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_35(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, None).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_36(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault([]).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_37(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, ).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_38(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = None

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_39(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) >= 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_40(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 2}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_41(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError(None)

    def xǁOneToOneǁ__init____mutmut_42(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' the following values: %r' / dupes)

    def xǁOneToOneǁ__init____mutmut_43(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('XXexpected unique values, got multiple keys forXX'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_44(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('EXPECTED UNIQUE VALUES, GOT MULTIPLE KEYS FOR'
                         ' the following values: %r' % dupes)

    def xǁOneToOneǁ__init____mutmut_45(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         'XX the following values: %rXX' % dupes)

    def xǁOneToOneǁ__init____mutmut_46(self, *a, **kw):
        raise_on_dupe = False
        if a:
            if a[0] is _OTO_INV_MARKER:
                self.inv = a[1]
                dict.__init__(self, [(v, k) for k, v in self.inv.items()])
                return
            elif a[0] is _OTO_UNIQUE_MARKER:
                a, raise_on_dupe = a[1:], True

        dict.__init__(self, *a, **kw)
        self.inv = self.__class__(_OTO_INV_MARKER, self)

        if len(self) == len(self.inv):
            # if lengths match, that means everything's unique
            return

        if not raise_on_dupe:
            dict.clear(self)
            dict.update(self, [(v, k) for k, v in self.inv.items()])
            return

        # generate an error message if the values aren't 1:1

        val_multidict = {}
        for k, v in self.items():
            val_multidict.setdefault(v, []).append(k)

        dupes = {v: k_list for v, k_list in
                      val_multidict.items() if len(k_list) > 1}

        raise ValueError('expected unique values, got multiple keys for'
                         ' THE FOLLOWING VALUES: %R' % dupes)
    
    xǁOneToOneǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁ__init____mutmut_1': xǁOneToOneǁ__init____mutmut_1, 
        'xǁOneToOneǁ__init____mutmut_2': xǁOneToOneǁ__init____mutmut_2, 
        'xǁOneToOneǁ__init____mutmut_3': xǁOneToOneǁ__init____mutmut_3, 
        'xǁOneToOneǁ__init____mutmut_4': xǁOneToOneǁ__init____mutmut_4, 
        'xǁOneToOneǁ__init____mutmut_5': xǁOneToOneǁ__init____mutmut_5, 
        'xǁOneToOneǁ__init____mutmut_6': xǁOneToOneǁ__init____mutmut_6, 
        'xǁOneToOneǁ__init____mutmut_7': xǁOneToOneǁ__init____mutmut_7, 
        'xǁOneToOneǁ__init____mutmut_8': xǁOneToOneǁ__init____mutmut_8, 
        'xǁOneToOneǁ__init____mutmut_9': xǁOneToOneǁ__init____mutmut_9, 
        'xǁOneToOneǁ__init____mutmut_10': xǁOneToOneǁ__init____mutmut_10, 
        'xǁOneToOneǁ__init____mutmut_11': xǁOneToOneǁ__init____mutmut_11, 
        'xǁOneToOneǁ__init____mutmut_12': xǁOneToOneǁ__init____mutmut_12, 
        'xǁOneToOneǁ__init____mutmut_13': xǁOneToOneǁ__init____mutmut_13, 
        'xǁOneToOneǁ__init____mutmut_14': xǁOneToOneǁ__init____mutmut_14, 
        'xǁOneToOneǁ__init____mutmut_15': xǁOneToOneǁ__init____mutmut_15, 
        'xǁOneToOneǁ__init____mutmut_16': xǁOneToOneǁ__init____mutmut_16, 
        'xǁOneToOneǁ__init____mutmut_17': xǁOneToOneǁ__init____mutmut_17, 
        'xǁOneToOneǁ__init____mutmut_18': xǁOneToOneǁ__init____mutmut_18, 
        'xǁOneToOneǁ__init____mutmut_19': xǁOneToOneǁ__init____mutmut_19, 
        'xǁOneToOneǁ__init____mutmut_20': xǁOneToOneǁ__init____mutmut_20, 
        'xǁOneToOneǁ__init____mutmut_21': xǁOneToOneǁ__init____mutmut_21, 
        'xǁOneToOneǁ__init____mutmut_22': xǁOneToOneǁ__init____mutmut_22, 
        'xǁOneToOneǁ__init____mutmut_23': xǁOneToOneǁ__init____mutmut_23, 
        'xǁOneToOneǁ__init____mutmut_24': xǁOneToOneǁ__init____mutmut_24, 
        'xǁOneToOneǁ__init____mutmut_25': xǁOneToOneǁ__init____mutmut_25, 
        'xǁOneToOneǁ__init____mutmut_26': xǁOneToOneǁ__init____mutmut_26, 
        'xǁOneToOneǁ__init____mutmut_27': xǁOneToOneǁ__init____mutmut_27, 
        'xǁOneToOneǁ__init____mutmut_28': xǁOneToOneǁ__init____mutmut_28, 
        'xǁOneToOneǁ__init____mutmut_29': xǁOneToOneǁ__init____mutmut_29, 
        'xǁOneToOneǁ__init____mutmut_30': xǁOneToOneǁ__init____mutmut_30, 
        'xǁOneToOneǁ__init____mutmut_31': xǁOneToOneǁ__init____mutmut_31, 
        'xǁOneToOneǁ__init____mutmut_32': xǁOneToOneǁ__init____mutmut_32, 
        'xǁOneToOneǁ__init____mutmut_33': xǁOneToOneǁ__init____mutmut_33, 
        'xǁOneToOneǁ__init____mutmut_34': xǁOneToOneǁ__init____mutmut_34, 
        'xǁOneToOneǁ__init____mutmut_35': xǁOneToOneǁ__init____mutmut_35, 
        'xǁOneToOneǁ__init____mutmut_36': xǁOneToOneǁ__init____mutmut_36, 
        'xǁOneToOneǁ__init____mutmut_37': xǁOneToOneǁ__init____mutmut_37, 
        'xǁOneToOneǁ__init____mutmut_38': xǁOneToOneǁ__init____mutmut_38, 
        'xǁOneToOneǁ__init____mutmut_39': xǁOneToOneǁ__init____mutmut_39, 
        'xǁOneToOneǁ__init____mutmut_40': xǁOneToOneǁ__init____mutmut_40, 
        'xǁOneToOneǁ__init____mutmut_41': xǁOneToOneǁ__init____mutmut_41, 
        'xǁOneToOneǁ__init____mutmut_42': xǁOneToOneǁ__init____mutmut_42, 
        'xǁOneToOneǁ__init____mutmut_43': xǁOneToOneǁ__init____mutmut_43, 
        'xǁOneToOneǁ__init____mutmut_44': xǁOneToOneǁ__init____mutmut_44, 
        'xǁOneToOneǁ__init____mutmut_45': xǁOneToOneǁ__init____mutmut_45, 
        'xǁOneToOneǁ__init____mutmut_46': xǁOneToOneǁ__init____mutmut_46
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁOneToOneǁ__init____mutmut_orig)
    xǁOneToOneǁ__init____mutmut_orig.__name__ = 'xǁOneToOneǁ__init__'

    @classmethod
    def unique(cls, *a, **kw):
        """This alternate constructor for OneToOne will raise an exception
        when input values overlap. For instance:

        >>> OneToOne.unique({'a': 1, 'b': 1})
        Traceback (most recent call last):
        ...
        ValueError: expected unique values, got multiple keys for the following values: ...

        This even works across inputs:

        >>> a_dict = {'a': 2}
        >>> OneToOne.unique(a_dict, b=2)
        Traceback (most recent call last):
        ...
        ValueError: expected unique values, got multiple keys for the following values: ...
        """
        return cls(_OTO_UNIQUE_MARKER, *a, **kw)

    def xǁOneToOneǁ__setitem____mutmut_orig(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_1(self, key, val):
        hash(None)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_2(self, key, val):
        hash(val)  # ensure val is a valid key
        if key not in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_3(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(None, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_4(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, None)
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_5(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_6(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, )
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_7(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val not in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_8(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(None, key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_9(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, None, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_10(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, None)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_11(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(key, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_12(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, val)
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_13(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, )
        dict.__setitem__(self.inv, val, key)

    def xǁOneToOneǁ__setitem____mutmut_14(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(None, val, key)

    def xǁOneToOneǁ__setitem____mutmut_15(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, None, key)

    def xǁOneToOneǁ__setitem____mutmut_16(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, None)

    def xǁOneToOneǁ__setitem____mutmut_17(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(val, key)

    def xǁOneToOneǁ__setitem____mutmut_18(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, key)

    def xǁOneToOneǁ__setitem____mutmut_19(self, key, val):
        hash(val)  # ensure val is a valid key
        if key in self:
            dict.__delitem__(self.inv, self[key])
        if val in self.inv:
            del self.inv[val]
        dict.__setitem__(self, key, val)
        dict.__setitem__(self.inv, val, )
    
    xǁOneToOneǁ__setitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁ__setitem____mutmut_1': xǁOneToOneǁ__setitem____mutmut_1, 
        'xǁOneToOneǁ__setitem____mutmut_2': xǁOneToOneǁ__setitem____mutmut_2, 
        'xǁOneToOneǁ__setitem____mutmut_3': xǁOneToOneǁ__setitem____mutmut_3, 
        'xǁOneToOneǁ__setitem____mutmut_4': xǁOneToOneǁ__setitem____mutmut_4, 
        'xǁOneToOneǁ__setitem____mutmut_5': xǁOneToOneǁ__setitem____mutmut_5, 
        'xǁOneToOneǁ__setitem____mutmut_6': xǁOneToOneǁ__setitem____mutmut_6, 
        'xǁOneToOneǁ__setitem____mutmut_7': xǁOneToOneǁ__setitem____mutmut_7, 
        'xǁOneToOneǁ__setitem____mutmut_8': xǁOneToOneǁ__setitem____mutmut_8, 
        'xǁOneToOneǁ__setitem____mutmut_9': xǁOneToOneǁ__setitem____mutmut_9, 
        'xǁOneToOneǁ__setitem____mutmut_10': xǁOneToOneǁ__setitem____mutmut_10, 
        'xǁOneToOneǁ__setitem____mutmut_11': xǁOneToOneǁ__setitem____mutmut_11, 
        'xǁOneToOneǁ__setitem____mutmut_12': xǁOneToOneǁ__setitem____mutmut_12, 
        'xǁOneToOneǁ__setitem____mutmut_13': xǁOneToOneǁ__setitem____mutmut_13, 
        'xǁOneToOneǁ__setitem____mutmut_14': xǁOneToOneǁ__setitem____mutmut_14, 
        'xǁOneToOneǁ__setitem____mutmut_15': xǁOneToOneǁ__setitem____mutmut_15, 
        'xǁOneToOneǁ__setitem____mutmut_16': xǁOneToOneǁ__setitem____mutmut_16, 
        'xǁOneToOneǁ__setitem____mutmut_17': xǁOneToOneǁ__setitem____mutmut_17, 
        'xǁOneToOneǁ__setitem____mutmut_18': xǁOneToOneǁ__setitem____mutmut_18, 
        'xǁOneToOneǁ__setitem____mutmut_19': xǁOneToOneǁ__setitem____mutmut_19
    }
    
    def __setitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁ__setitem____mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁ__setitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setitem__.__signature__ = _mutmut_signature(xǁOneToOneǁ__setitem____mutmut_orig)
    xǁOneToOneǁ__setitem____mutmut_orig.__name__ = 'xǁOneToOneǁ__setitem__'

    def xǁOneToOneǁ__delitem____mutmut_orig(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(self, key)

    def xǁOneToOneǁ__delitem____mutmut_1(self, key):
        dict.__delitem__(None, self[key])
        dict.__delitem__(self, key)

    def xǁOneToOneǁ__delitem____mutmut_2(self, key):
        dict.__delitem__(self.inv, None)
        dict.__delitem__(self, key)

    def xǁOneToOneǁ__delitem____mutmut_3(self, key):
        dict.__delitem__(self[key])
        dict.__delitem__(self, key)

    def xǁOneToOneǁ__delitem____mutmut_4(self, key):
        dict.__delitem__(self.inv, )
        dict.__delitem__(self, key)

    def xǁOneToOneǁ__delitem____mutmut_5(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(None, key)

    def xǁOneToOneǁ__delitem____mutmut_6(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(self, None)

    def xǁOneToOneǁ__delitem____mutmut_7(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(key)

    def xǁOneToOneǁ__delitem____mutmut_8(self, key):
        dict.__delitem__(self.inv, self[key])
        dict.__delitem__(self, )
    
    xǁOneToOneǁ__delitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁ__delitem____mutmut_1': xǁOneToOneǁ__delitem____mutmut_1, 
        'xǁOneToOneǁ__delitem____mutmut_2': xǁOneToOneǁ__delitem____mutmut_2, 
        'xǁOneToOneǁ__delitem____mutmut_3': xǁOneToOneǁ__delitem____mutmut_3, 
        'xǁOneToOneǁ__delitem____mutmut_4': xǁOneToOneǁ__delitem____mutmut_4, 
        'xǁOneToOneǁ__delitem____mutmut_5': xǁOneToOneǁ__delitem____mutmut_5, 
        'xǁOneToOneǁ__delitem____mutmut_6': xǁOneToOneǁ__delitem____mutmut_6, 
        'xǁOneToOneǁ__delitem____mutmut_7': xǁOneToOneǁ__delitem____mutmut_7, 
        'xǁOneToOneǁ__delitem____mutmut_8': xǁOneToOneǁ__delitem____mutmut_8
    }
    
    def __delitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁ__delitem____mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁ__delitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delitem__.__signature__ = _mutmut_signature(xǁOneToOneǁ__delitem____mutmut_orig)
    xǁOneToOneǁ__delitem____mutmut_orig.__name__ = 'xǁOneToOneǁ__delitem__'

    def xǁOneToOneǁclear__mutmut_orig(self):
        dict.clear(self)
        dict.clear(self.inv)

    def xǁOneToOneǁclear__mutmut_1(self):
        dict.clear(None)
        dict.clear(self.inv)

    def xǁOneToOneǁclear__mutmut_2(self):
        dict.clear(self)
        dict.clear(None)
    
    xǁOneToOneǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁclear__mutmut_1': xǁOneToOneǁclear__mutmut_1, 
        'xǁOneToOneǁclear__mutmut_2': xǁOneToOneǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁclear__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁOneToOneǁclear__mutmut_orig)
    xǁOneToOneǁclear__mutmut_orig.__name__ = 'xǁOneToOneǁclear'

    def xǁOneToOneǁcopy__mutmut_orig(self):
        return self.__class__(self)

    def xǁOneToOneǁcopy__mutmut_1(self):
        return self.__class__(None)
    
    xǁOneToOneǁcopy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁcopy__mutmut_1': xǁOneToOneǁcopy__mutmut_1
    }
    
    def copy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁcopy__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁcopy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    copy.__signature__ = _mutmut_signature(xǁOneToOneǁcopy__mutmut_orig)
    xǁOneToOneǁcopy__mutmut_orig.__name__ = 'xǁOneToOneǁcopy'

    def xǁOneToOneǁpop__mutmut_orig(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_1(self, key, default=_MISSING):
        if key not in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_2(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(None, self[key])
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_3(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, None)
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_4(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self[key])
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_5(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, )
            return dict.pop(self, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_6(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(None, key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_7(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, None)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_8(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(key)
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_9(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, )
        if default is not _MISSING:
            return default
        raise KeyError()

    def xǁOneToOneǁpop__mutmut_10(self, key, default=_MISSING):
        if key in self:
            dict.__delitem__(self.inv, self[key])
            return dict.pop(self, key)
        if default is _MISSING:
            return default
        raise KeyError()
    
    xǁOneToOneǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁpop__mutmut_1': xǁOneToOneǁpop__mutmut_1, 
        'xǁOneToOneǁpop__mutmut_2': xǁOneToOneǁpop__mutmut_2, 
        'xǁOneToOneǁpop__mutmut_3': xǁOneToOneǁpop__mutmut_3, 
        'xǁOneToOneǁpop__mutmut_4': xǁOneToOneǁpop__mutmut_4, 
        'xǁOneToOneǁpop__mutmut_5': xǁOneToOneǁpop__mutmut_5, 
        'xǁOneToOneǁpop__mutmut_6': xǁOneToOneǁpop__mutmut_6, 
        'xǁOneToOneǁpop__mutmut_7': xǁOneToOneǁpop__mutmut_7, 
        'xǁOneToOneǁpop__mutmut_8': xǁOneToOneǁpop__mutmut_8, 
        'xǁOneToOneǁpop__mutmut_9': xǁOneToOneǁpop__mutmut_9, 
        'xǁOneToOneǁpop__mutmut_10': xǁOneToOneǁpop__mutmut_10
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁpop__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁOneToOneǁpop__mutmut_orig)
    xǁOneToOneǁpop__mutmut_orig.__name__ = 'xǁOneToOneǁpop'

    def xǁOneToOneǁpopitem__mutmut_orig(self):
        key, val = dict.popitem(self)
        dict.__delitem__(self.inv, val)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_1(self):
        key, val = None
        dict.__delitem__(self.inv, val)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_2(self):
        key, val = dict.popitem(None)
        dict.__delitem__(self.inv, val)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_3(self):
        key, val = dict.popitem(self)
        dict.__delitem__(None, val)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_4(self):
        key, val = dict.popitem(self)
        dict.__delitem__(self.inv, None)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_5(self):
        key, val = dict.popitem(self)
        dict.__delitem__(val)
        return key, val

    def xǁOneToOneǁpopitem__mutmut_6(self):
        key, val = dict.popitem(self)
        dict.__delitem__(self.inv, )
        return key, val
    
    xǁOneToOneǁpopitem__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁpopitem__mutmut_1': xǁOneToOneǁpopitem__mutmut_1, 
        'xǁOneToOneǁpopitem__mutmut_2': xǁOneToOneǁpopitem__mutmut_2, 
        'xǁOneToOneǁpopitem__mutmut_3': xǁOneToOneǁpopitem__mutmut_3, 
        'xǁOneToOneǁpopitem__mutmut_4': xǁOneToOneǁpopitem__mutmut_4, 
        'xǁOneToOneǁpopitem__mutmut_5': xǁOneToOneǁpopitem__mutmut_5, 
        'xǁOneToOneǁpopitem__mutmut_6': xǁOneToOneǁpopitem__mutmut_6
    }
    
    def popitem(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁpopitem__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁpopitem__mutmut_mutants"), args, kwargs, self)
        return result 
    
    popitem.__signature__ = _mutmut_signature(xǁOneToOneǁpopitem__mutmut_orig)
    xǁOneToOneǁpopitem__mutmut_orig.__name__ = 'xǁOneToOneǁpopitem'

    def xǁOneToOneǁsetdefault__mutmut_orig(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def xǁOneToOneǁsetdefault__mutmut_1(self, key, default=None):
        if key in self:
            self[key] = default
        return self[key]

    def xǁOneToOneǁsetdefault__mutmut_2(self, key, default=None):
        if key not in self:
            self[key] = None
        return self[key]
    
    xǁOneToOneǁsetdefault__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁsetdefault__mutmut_1': xǁOneToOneǁsetdefault__mutmut_1, 
        'xǁOneToOneǁsetdefault__mutmut_2': xǁOneToOneǁsetdefault__mutmut_2
    }
    
    def setdefault(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁsetdefault__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁsetdefault__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setdefault.__signature__ = _mutmut_signature(xǁOneToOneǁsetdefault__mutmut_orig)
    xǁOneToOneǁsetdefault__mutmut_orig.__name__ = 'xǁOneToOneǁsetdefault'

    def xǁOneToOneǁupdate__mutmut_orig(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_1(self, dict_or_iterable, **kw):
        keys_vals = None
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_2(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(None)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_3(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = None
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_4(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(None)
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_5(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(None)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_6(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(None)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_7(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = None
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_8(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(None)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_9(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(None)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_10(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(None)
        for key, val in keys_vals:
            self[key] = val

    def xǁOneToOneǁupdate__mutmut_11(self, dict_or_iterable, **kw):
        keys_vals = []
        if isinstance(dict_or_iterable, dict):
            for val in dict_or_iterable.values():
                hash(val)
                keys_vals = list(dict_or_iterable.items())
        else:
            for key, val in dict_or_iterable:
                hash(key)
                hash(val)
                keys_vals = list(dict_or_iterable)
        for val in kw.values():
            hash(val)
        keys_vals.extend(kw.items())
        for key, val in keys_vals:
            self[key] = None
    
    xǁOneToOneǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁupdate__mutmut_1': xǁOneToOneǁupdate__mutmut_1, 
        'xǁOneToOneǁupdate__mutmut_2': xǁOneToOneǁupdate__mutmut_2, 
        'xǁOneToOneǁupdate__mutmut_3': xǁOneToOneǁupdate__mutmut_3, 
        'xǁOneToOneǁupdate__mutmut_4': xǁOneToOneǁupdate__mutmut_4, 
        'xǁOneToOneǁupdate__mutmut_5': xǁOneToOneǁupdate__mutmut_5, 
        'xǁOneToOneǁupdate__mutmut_6': xǁOneToOneǁupdate__mutmut_6, 
        'xǁOneToOneǁupdate__mutmut_7': xǁOneToOneǁupdate__mutmut_7, 
        'xǁOneToOneǁupdate__mutmut_8': xǁOneToOneǁupdate__mutmut_8, 
        'xǁOneToOneǁupdate__mutmut_9': xǁOneToOneǁupdate__mutmut_9, 
        'xǁOneToOneǁupdate__mutmut_10': xǁOneToOneǁupdate__mutmut_10, 
        'xǁOneToOneǁupdate__mutmut_11': xǁOneToOneǁupdate__mutmut_11
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁOneToOneǁupdate__mutmut_orig)
    xǁOneToOneǁupdate__mutmut_orig.__name__ = 'xǁOneToOneǁupdate'

    def xǁOneToOneǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        dict_repr = dict.__repr__(self)
        return f"{cn}({dict_repr})"

    def xǁOneToOneǁ__repr____mutmut_1(self):
        cn = None
        dict_repr = dict.__repr__(self)
        return f"{cn}({dict_repr})"

    def xǁOneToOneǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        dict_repr = None
        return f"{cn}({dict_repr})"

    def xǁOneToOneǁ__repr____mutmut_3(self):
        cn = self.__class__.__name__
        dict_repr = dict.__repr__(None)
        return f"{cn}({dict_repr})"
    
    xǁOneToOneǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOneToOneǁ__repr____mutmut_1': xǁOneToOneǁ__repr____mutmut_1, 
        'xǁOneToOneǁ__repr____mutmut_2': xǁOneToOneǁ__repr____mutmut_2, 
        'xǁOneToOneǁ__repr____mutmut_3': xǁOneToOneǁ__repr____mutmut_3
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOneToOneǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁOneToOneǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁOneToOneǁ__repr____mutmut_orig)
    xǁOneToOneǁ__repr____mutmut_orig.__name__ = 'xǁOneToOneǁ__repr__'


# marker for the secret handshake used internally to set up the invert ManyToMany
_PAIRING = object()


class ManyToMany:
    """
    a dict-like entity that represents a many-to-many relationship
    between two groups of objects

    behaves like a dict-of-tuples; also has .inv which is kept
    up to date which is a dict-of-tuples in the other direction

    also, can be used as a directed graph among hashable python objects
    """
    def xǁManyToManyǁ__init____mutmut_orig(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_1(self, items=None):
        self.data = None
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_2(self, items=None):
        self.data = {}
        if type(items) is tuple and items or items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_3(self, items=None):
        self.data = {}
        if type(items) is tuple or items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_4(self, items=None):
        self.data = {}
        if type(None) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_5(self, items=None):
        self.data = {}
        if type(items) is not tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_6(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[1] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_7(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is not _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_8(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = None
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_9(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[2]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_10(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = None
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_11(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__(None)
            if items:
                self.update(items)
        return
    def xǁManyToManyǁ__init____mutmut_12(self, items=None):
        self.data = {}
        if type(items) is tuple and items and items[0] is _PAIRING:
            self.inv = items[1]
        else:
            self.inv = self.__class__((_PAIRING, self))
            if items:
                self.update(None)
        return
    
    xǁManyToManyǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__init____mutmut_1': xǁManyToManyǁ__init____mutmut_1, 
        'xǁManyToManyǁ__init____mutmut_2': xǁManyToManyǁ__init____mutmut_2, 
        'xǁManyToManyǁ__init____mutmut_3': xǁManyToManyǁ__init____mutmut_3, 
        'xǁManyToManyǁ__init____mutmut_4': xǁManyToManyǁ__init____mutmut_4, 
        'xǁManyToManyǁ__init____mutmut_5': xǁManyToManyǁ__init____mutmut_5, 
        'xǁManyToManyǁ__init____mutmut_6': xǁManyToManyǁ__init____mutmut_6, 
        'xǁManyToManyǁ__init____mutmut_7': xǁManyToManyǁ__init____mutmut_7, 
        'xǁManyToManyǁ__init____mutmut_8': xǁManyToManyǁ__init____mutmut_8, 
        'xǁManyToManyǁ__init____mutmut_9': xǁManyToManyǁ__init____mutmut_9, 
        'xǁManyToManyǁ__init____mutmut_10': xǁManyToManyǁ__init____mutmut_10, 
        'xǁManyToManyǁ__init____mutmut_11': xǁManyToManyǁ__init____mutmut_11, 
        'xǁManyToManyǁ__init____mutmut_12': xǁManyToManyǁ__init____mutmut_12
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁManyToManyǁ__init____mutmut_orig)
    xǁManyToManyǁ__init____mutmut_orig.__name__ = 'xǁManyToManyǁ__init__'

    def get(self, key, default=frozenset()):
        try:
            return self[key]
        except KeyError:
            return default

    def xǁManyToManyǁ__getitem____mutmut_orig(self, key):
        return frozenset(self.data[key])

    def xǁManyToManyǁ__getitem____mutmut_1(self, key):
        return frozenset(None)
    
    xǁManyToManyǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__getitem____mutmut_1': xǁManyToManyǁ__getitem____mutmut_1
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁManyToManyǁ__getitem____mutmut_orig)
    xǁManyToManyǁ__getitem____mutmut_orig.__name__ = 'xǁManyToManyǁ__getitem__'

    def xǁManyToManyǁ__setitem____mutmut_orig(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_1(self, key, vals):
        vals = None
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_2(self, key, vals):
        vals = set(None)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_3(self, key, vals):
        vals = set(vals)
        if key not in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_4(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = None
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_5(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] + vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_6(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals = self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_7(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals += self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_8(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(None, val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_9(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, None)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_10(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(val)
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_11(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, )
        for val in vals:
            self.add(key, val)

    def xǁManyToManyǁ__setitem____mutmut_12(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(None, val)

    def xǁManyToManyǁ__setitem____mutmut_13(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, None)

    def xǁManyToManyǁ__setitem____mutmut_14(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(val)

    def xǁManyToManyǁ__setitem____mutmut_15(self, key, vals):
        vals = set(vals)
        if key in self:
            to_remove = self.data[key] - vals
            vals -= self.data[key]
            for val in to_remove:
                self.remove(key, val)
        for val in vals:
            self.add(key, )
    
    xǁManyToManyǁ__setitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__setitem____mutmut_1': xǁManyToManyǁ__setitem____mutmut_1, 
        'xǁManyToManyǁ__setitem____mutmut_2': xǁManyToManyǁ__setitem____mutmut_2, 
        'xǁManyToManyǁ__setitem____mutmut_3': xǁManyToManyǁ__setitem____mutmut_3, 
        'xǁManyToManyǁ__setitem____mutmut_4': xǁManyToManyǁ__setitem____mutmut_4, 
        'xǁManyToManyǁ__setitem____mutmut_5': xǁManyToManyǁ__setitem____mutmut_5, 
        'xǁManyToManyǁ__setitem____mutmut_6': xǁManyToManyǁ__setitem____mutmut_6, 
        'xǁManyToManyǁ__setitem____mutmut_7': xǁManyToManyǁ__setitem____mutmut_7, 
        'xǁManyToManyǁ__setitem____mutmut_8': xǁManyToManyǁ__setitem____mutmut_8, 
        'xǁManyToManyǁ__setitem____mutmut_9': xǁManyToManyǁ__setitem____mutmut_9, 
        'xǁManyToManyǁ__setitem____mutmut_10': xǁManyToManyǁ__setitem____mutmut_10, 
        'xǁManyToManyǁ__setitem____mutmut_11': xǁManyToManyǁ__setitem____mutmut_11, 
        'xǁManyToManyǁ__setitem____mutmut_12': xǁManyToManyǁ__setitem____mutmut_12, 
        'xǁManyToManyǁ__setitem____mutmut_13': xǁManyToManyǁ__setitem____mutmut_13, 
        'xǁManyToManyǁ__setitem____mutmut_14': xǁManyToManyǁ__setitem____mutmut_14, 
        'xǁManyToManyǁ__setitem____mutmut_15': xǁManyToManyǁ__setitem____mutmut_15
    }
    
    def __setitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__setitem____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__setitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __setitem__.__signature__ = _mutmut_signature(xǁManyToManyǁ__setitem____mutmut_orig)
    xǁManyToManyǁ__setitem____mutmut_orig.__name__ = 'xǁManyToManyǁ__setitem__'

    def xǁManyToManyǁ__delitem____mutmut_orig(self, key):
        for val in self.data.pop(key):
            self.inv.data[val].remove(key)
            if not self.inv.data[val]:
                del self.inv.data[val]

    def xǁManyToManyǁ__delitem____mutmut_1(self, key):
        for val in self.data.pop(None):
            self.inv.data[val].remove(key)
            if not self.inv.data[val]:
                del self.inv.data[val]

    def xǁManyToManyǁ__delitem____mutmut_2(self, key):
        for val in self.data.pop(key):
            self.inv.data[val].remove(None)
            if not self.inv.data[val]:
                del self.inv.data[val]

    def xǁManyToManyǁ__delitem____mutmut_3(self, key):
        for val in self.data.pop(key):
            self.inv.data[val].remove(key)
            if self.inv.data[val]:
                del self.inv.data[val]
    
    xǁManyToManyǁ__delitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__delitem____mutmut_1': xǁManyToManyǁ__delitem____mutmut_1, 
        'xǁManyToManyǁ__delitem____mutmut_2': xǁManyToManyǁ__delitem____mutmut_2, 
        'xǁManyToManyǁ__delitem____mutmut_3': xǁManyToManyǁ__delitem____mutmut_3
    }
    
    def __delitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__delitem____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__delitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delitem__.__signature__ = _mutmut_signature(xǁManyToManyǁ__delitem____mutmut_orig)
    xǁManyToManyǁ__delitem____mutmut_orig.__name__ = 'xǁManyToManyǁ__delitem__'

    def xǁManyToManyǁupdate__mutmut_orig(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_1(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(None) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_2(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is not type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_3(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(None):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_4(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = None
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_5(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_6(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = None
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_7(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(None)
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_8(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_9(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = None
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_10(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(None)
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_11(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(None):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_12(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(None, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_13(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, None, None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_14(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr('keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_15(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_16(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', )):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_17(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'XXkeysXX', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_18(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'KEYS', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_19(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(None, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_20(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, None)
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_21(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(iterable[k])
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_22(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, )
        else:
            for key, val in iterable:
                self.add(key, val)
        return

    def xǁManyToManyǁupdate__mutmut_23(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(None, val)
        return

    def xǁManyToManyǁupdate__mutmut_24(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, None)
        return

    def xǁManyToManyǁupdate__mutmut_25(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(val)
        return

    def xǁManyToManyǁupdate__mutmut_26(self, iterable):
        """given an iterable of (key, val), add them all"""
        if type(iterable) is type(self):
            other = iterable
            for k in other.data:
                if k not in self.data:
                    self.data[k] = other.data[k]
                else:
                    self.data[k].update(other.data[k])
            for k in other.inv.data:
                if k not in self.inv.data:
                    self.inv.data[k] = other.inv.data[k]
                else:
                    self.inv.data[k].update(other.inv.data[k])
        elif callable(getattr(iterable, 'keys', None)):
            for k in iterable.keys():
                self.add(k, iterable[k])
        else:
            for key, val in iterable:
                self.add(key, )
        return
    
    xǁManyToManyǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁupdate__mutmut_1': xǁManyToManyǁupdate__mutmut_1, 
        'xǁManyToManyǁupdate__mutmut_2': xǁManyToManyǁupdate__mutmut_2, 
        'xǁManyToManyǁupdate__mutmut_3': xǁManyToManyǁupdate__mutmut_3, 
        'xǁManyToManyǁupdate__mutmut_4': xǁManyToManyǁupdate__mutmut_4, 
        'xǁManyToManyǁupdate__mutmut_5': xǁManyToManyǁupdate__mutmut_5, 
        'xǁManyToManyǁupdate__mutmut_6': xǁManyToManyǁupdate__mutmut_6, 
        'xǁManyToManyǁupdate__mutmut_7': xǁManyToManyǁupdate__mutmut_7, 
        'xǁManyToManyǁupdate__mutmut_8': xǁManyToManyǁupdate__mutmut_8, 
        'xǁManyToManyǁupdate__mutmut_9': xǁManyToManyǁupdate__mutmut_9, 
        'xǁManyToManyǁupdate__mutmut_10': xǁManyToManyǁupdate__mutmut_10, 
        'xǁManyToManyǁupdate__mutmut_11': xǁManyToManyǁupdate__mutmut_11, 
        'xǁManyToManyǁupdate__mutmut_12': xǁManyToManyǁupdate__mutmut_12, 
        'xǁManyToManyǁupdate__mutmut_13': xǁManyToManyǁupdate__mutmut_13, 
        'xǁManyToManyǁupdate__mutmut_14': xǁManyToManyǁupdate__mutmut_14, 
        'xǁManyToManyǁupdate__mutmut_15': xǁManyToManyǁupdate__mutmut_15, 
        'xǁManyToManyǁupdate__mutmut_16': xǁManyToManyǁupdate__mutmut_16, 
        'xǁManyToManyǁupdate__mutmut_17': xǁManyToManyǁupdate__mutmut_17, 
        'xǁManyToManyǁupdate__mutmut_18': xǁManyToManyǁupdate__mutmut_18, 
        'xǁManyToManyǁupdate__mutmut_19': xǁManyToManyǁupdate__mutmut_19, 
        'xǁManyToManyǁupdate__mutmut_20': xǁManyToManyǁupdate__mutmut_20, 
        'xǁManyToManyǁupdate__mutmut_21': xǁManyToManyǁupdate__mutmut_21, 
        'xǁManyToManyǁupdate__mutmut_22': xǁManyToManyǁupdate__mutmut_22, 
        'xǁManyToManyǁupdate__mutmut_23': xǁManyToManyǁupdate__mutmut_23, 
        'xǁManyToManyǁupdate__mutmut_24': xǁManyToManyǁupdate__mutmut_24, 
        'xǁManyToManyǁupdate__mutmut_25': xǁManyToManyǁupdate__mutmut_25, 
        'xǁManyToManyǁupdate__mutmut_26': xǁManyToManyǁupdate__mutmut_26
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁManyToManyǁupdate__mutmut_orig)
    xǁManyToManyǁupdate__mutmut_orig.__name__ = 'xǁManyToManyǁupdate'

    def xǁManyToManyǁadd__mutmut_orig(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_1(self, key, val):
        if key in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_2(self, key, val):
        if key not in self.data:
            self.data[key] = None
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_3(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(None)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_4(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_5(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = None
        self.inv.data[val].add(key)

    def xǁManyToManyǁadd__mutmut_6(self, key, val):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(val)
        if val not in self.inv.data:
            self.inv.data[val] = set()
        self.inv.data[val].add(None)
    
    xǁManyToManyǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁadd__mutmut_1': xǁManyToManyǁadd__mutmut_1, 
        'xǁManyToManyǁadd__mutmut_2': xǁManyToManyǁadd__mutmut_2, 
        'xǁManyToManyǁadd__mutmut_3': xǁManyToManyǁadd__mutmut_3, 
        'xǁManyToManyǁadd__mutmut_4': xǁManyToManyǁadd__mutmut_4, 
        'xǁManyToManyǁadd__mutmut_5': xǁManyToManyǁadd__mutmut_5, 
        'xǁManyToManyǁadd__mutmut_6': xǁManyToManyǁadd__mutmut_6
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁadd__mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁManyToManyǁadd__mutmut_orig)
    xǁManyToManyǁadd__mutmut_orig.__name__ = 'xǁManyToManyǁadd'

    def xǁManyToManyǁremove__mutmut_orig(self, key, val):
        self.data[key].remove(val)
        if not self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(key)
        if not self.inv.data[val]:
            del self.inv.data[val]

    def xǁManyToManyǁremove__mutmut_1(self, key, val):
        self.data[key].remove(None)
        if not self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(key)
        if not self.inv.data[val]:
            del self.inv.data[val]

    def xǁManyToManyǁremove__mutmut_2(self, key, val):
        self.data[key].remove(val)
        if self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(key)
        if not self.inv.data[val]:
            del self.inv.data[val]

    def xǁManyToManyǁremove__mutmut_3(self, key, val):
        self.data[key].remove(val)
        if not self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(None)
        if not self.inv.data[val]:
            del self.inv.data[val]

    def xǁManyToManyǁremove__mutmut_4(self, key, val):
        self.data[key].remove(val)
        if not self.data[key]:
            del self.data[key]
        self.inv.data[val].remove(key)
        if self.inv.data[val]:
            del self.inv.data[val]
    
    xǁManyToManyǁremove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁremove__mutmut_1': xǁManyToManyǁremove__mutmut_1, 
        'xǁManyToManyǁremove__mutmut_2': xǁManyToManyǁremove__mutmut_2, 
        'xǁManyToManyǁremove__mutmut_3': xǁManyToManyǁremove__mutmut_3, 
        'xǁManyToManyǁremove__mutmut_4': xǁManyToManyǁremove__mutmut_4
    }
    
    def remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁremove__mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁremove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    remove.__signature__ = _mutmut_signature(xǁManyToManyǁremove__mutmut_orig)
    xǁManyToManyǁremove__mutmut_orig.__name__ = 'xǁManyToManyǁremove'

    def xǁManyToManyǁreplace__mutmut_orig(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_1(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_2(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = None
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_3(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(None)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_4(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = None
            revset.remove(key)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_5(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(None)
            revset.add(newkey)

    def xǁManyToManyǁreplace__mutmut_6(self, key, newkey):
        """
        replace instances of key by newkey
        """
        if key not in self.data:
            return
        self.data[newkey] = fwdset = self.data.pop(key)
        for val in fwdset:
            revset = self.inv.data[val]
            revset.remove(key)
            revset.add(None)
    
    xǁManyToManyǁreplace__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁreplace__mutmut_1': xǁManyToManyǁreplace__mutmut_1, 
        'xǁManyToManyǁreplace__mutmut_2': xǁManyToManyǁreplace__mutmut_2, 
        'xǁManyToManyǁreplace__mutmut_3': xǁManyToManyǁreplace__mutmut_3, 
        'xǁManyToManyǁreplace__mutmut_4': xǁManyToManyǁreplace__mutmut_4, 
        'xǁManyToManyǁreplace__mutmut_5': xǁManyToManyǁreplace__mutmut_5, 
        'xǁManyToManyǁreplace__mutmut_6': xǁManyToManyǁreplace__mutmut_6
    }
    
    def replace(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁreplace__mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁreplace__mutmut_mutants"), args, kwargs, self)
        return result 
    
    replace.__signature__ = _mutmut_signature(xǁManyToManyǁreplace__mutmut_orig)
    xǁManyToManyǁreplace__mutmut_orig.__name__ = 'xǁManyToManyǁreplace'

    def iteritems(self):
        for key in self.data:
            for val in self.data[key]:
                yield key, val

    def keys(self):
        return self.data.keys()

    def xǁManyToManyǁ__contains____mutmut_orig(self, key):
        return key in self.data

    def xǁManyToManyǁ__contains____mutmut_1(self, key):
        return key not in self.data
    
    xǁManyToManyǁ__contains____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__contains____mutmut_1': xǁManyToManyǁ__contains____mutmut_1
    }
    
    def __contains__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__contains____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__contains____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __contains__.__signature__ = _mutmut_signature(xǁManyToManyǁ__contains____mutmut_orig)
    xǁManyToManyǁ__contains____mutmut_orig.__name__ = 'xǁManyToManyǁ__contains__'

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def xǁManyToManyǁ__eq____mutmut_orig(self, other):
        return type(self) == type(other) and self.data == other.data

    def xǁManyToManyǁ__eq____mutmut_1(self, other):
        return type(self) == type(other) or self.data == other.data

    def xǁManyToManyǁ__eq____mutmut_2(self, other):
        return type(None) == type(other) and self.data == other.data

    def xǁManyToManyǁ__eq____mutmut_3(self, other):
        return type(self) != type(other) and self.data == other.data

    def xǁManyToManyǁ__eq____mutmut_4(self, other):
        return type(self) == type(None) and self.data == other.data

    def xǁManyToManyǁ__eq____mutmut_5(self, other):
        return type(self) == type(other) and self.data != other.data
    
    xǁManyToManyǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__eq____mutmut_1': xǁManyToManyǁ__eq____mutmut_1, 
        'xǁManyToManyǁ__eq____mutmut_2': xǁManyToManyǁ__eq____mutmut_2, 
        'xǁManyToManyǁ__eq____mutmut_3': xǁManyToManyǁ__eq____mutmut_3, 
        'xǁManyToManyǁ__eq____mutmut_4': xǁManyToManyǁ__eq____mutmut_4, 
        'xǁManyToManyǁ__eq____mutmut_5': xǁManyToManyǁ__eq____mutmut_5
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁManyToManyǁ__eq____mutmut_orig)
    xǁManyToManyǁ__eq____mutmut_orig.__name__ = 'xǁManyToManyǁ__eq__'

    def xǁManyToManyǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return f'{cn}({list(self.iteritems())!r})'

    def xǁManyToManyǁ__repr____mutmut_1(self):
        cn = None
        return f'{cn}({list(self.iteritems())!r})'

    def xǁManyToManyǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        return f'{cn}({list(None)!r})'
    
    xǁManyToManyǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁManyToManyǁ__repr____mutmut_1': xǁManyToManyǁ__repr____mutmut_1, 
        'xǁManyToManyǁ__repr____mutmut_2': xǁManyToManyǁ__repr____mutmut_2
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁManyToManyǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁManyToManyǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁManyToManyǁ__repr____mutmut_orig)
    xǁManyToManyǁ__repr____mutmut_orig.__name__ = 'xǁManyToManyǁ__repr__'


def x_subdict__mutmut_orig(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_1(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is not None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_2(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = None
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_3(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is not None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_4(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = None

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_5(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = None

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_6(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) + set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_7(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(None) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_8(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(None)

    return type(d)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_9(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)(None)


def x_subdict__mutmut_10(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(None)([(k, v) for k, v in d.items() if k in keys])


def x_subdict__mutmut_11(d, keep=None, drop=None):
    """Compute the "subdictionary" of a dict, *d*.

    A subdict is to a dict what a subset is a to set. If *A* is a
    subdict of *B*, that means that all keys of *A* are present in
    *B*.

    Returns a new dict with any keys in *drop* removed, and any keys
    in *keep* still present, provided they were in the original
    dict. *keep* defaults to all keys, *drop* defaults to empty, so
    without one of these arguments, calling this function is
    equivalent to calling ``dict()``.

    >>> from pprint import pprint as pp
    >>> pp(subdict({'a': 1, 'b': 2}))
    {'a': 1, 'b': 2}
    >>> subdict({'a': 1, 'b': 2, 'c': 3}, drop=['b', 'c'])
    {'a': 1}
    >>> pp(subdict({'a': 1, 'b': 2, 'c': 3}, keep=['a', 'c']))
    {'a': 1, 'c': 3}

    """
    if keep is None:
        keep = d.keys()
    if drop is None:
        drop = []

    keys = set(keep) - set(drop)

    return type(d)([(k, v) for k, v in d.items() if k not in keys])

x_subdict__mutmut_mutants : ClassVar[MutantDict] = {
'x_subdict__mutmut_1': x_subdict__mutmut_1, 
    'x_subdict__mutmut_2': x_subdict__mutmut_2, 
    'x_subdict__mutmut_3': x_subdict__mutmut_3, 
    'x_subdict__mutmut_4': x_subdict__mutmut_4, 
    'x_subdict__mutmut_5': x_subdict__mutmut_5, 
    'x_subdict__mutmut_6': x_subdict__mutmut_6, 
    'x_subdict__mutmut_7': x_subdict__mutmut_7, 
    'x_subdict__mutmut_8': x_subdict__mutmut_8, 
    'x_subdict__mutmut_9': x_subdict__mutmut_9, 
    'x_subdict__mutmut_10': x_subdict__mutmut_10, 
    'x_subdict__mutmut_11': x_subdict__mutmut_11
}

def subdict(*args, **kwargs):
    result = _mutmut_trampoline(x_subdict__mutmut_orig, x_subdict__mutmut_mutants, args, kwargs)
    return result 

subdict.__signature__ = _mutmut_signature(x_subdict__mutmut_orig)
x_subdict__mutmut_orig.__name__ = 'x_subdict'


class FrozenHashError(TypeError):
    pass


class FrozenDict(dict):
    """An immutable dict subtype that is hashable and can itself be used
    as a :class:`dict` key or :class:`set` entry. What
    :class:`frozenset` is to :class:`set`, FrozenDict is to
    :class:`dict`.

    There was once an attempt to introduce such a type to the standard
    library, but it was rejected: `PEP 416 <https://www.python.org/dev/peps/pep-0416/>`_.

    Because FrozenDict is a :class:`dict` subtype, it automatically
    works everywhere a dict would, including JSON serialization.

    """
    __slots__ = ('_hash',)

    def xǁFrozenDictǁupdated__mutmut_orig(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(*a, **kw)
        return type(self)(data)

    def xǁFrozenDictǁupdated__mutmut_1(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = None
        data.update(*a, **kw)
        return type(self)(data)

    def xǁFrozenDictǁupdated__mutmut_2(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(None)
        data.update(*a, **kw)
        return type(self)(data)

    def xǁFrozenDictǁupdated__mutmut_3(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(**kw)
        return type(self)(data)

    def xǁFrozenDictǁupdated__mutmut_4(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(*a, )
        return type(self)(data)

    def xǁFrozenDictǁupdated__mutmut_5(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(*a, **kw)
        return type(self)(None)

    def xǁFrozenDictǁupdated__mutmut_6(self, *a, **kw):
        """Make a copy and add items from a dictionary or iterable (and/or
        keyword arguments), overwriting values under an existing
        key. See :meth:`dict.update` for more details.
        """
        data = dict(self)
        data.update(*a, **kw)
        return type(None)(data)
    
    xǁFrozenDictǁupdated__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFrozenDictǁupdated__mutmut_1': xǁFrozenDictǁupdated__mutmut_1, 
        'xǁFrozenDictǁupdated__mutmut_2': xǁFrozenDictǁupdated__mutmut_2, 
        'xǁFrozenDictǁupdated__mutmut_3': xǁFrozenDictǁupdated__mutmut_3, 
        'xǁFrozenDictǁupdated__mutmut_4': xǁFrozenDictǁupdated__mutmut_4, 
        'xǁFrozenDictǁupdated__mutmut_5': xǁFrozenDictǁupdated__mutmut_5, 
        'xǁFrozenDictǁupdated__mutmut_6': xǁFrozenDictǁupdated__mutmut_6
    }
    
    def updated(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFrozenDictǁupdated__mutmut_orig"), object.__getattribute__(self, "xǁFrozenDictǁupdated__mutmut_mutants"), args, kwargs, self)
        return result 
    
    updated.__signature__ = _mutmut_signature(xǁFrozenDictǁupdated__mutmut_orig)
    xǁFrozenDictǁupdated__mutmut_orig.__name__ = 'xǁFrozenDictǁupdated'

    @classmethod
    def fromkeys(cls, keys, value=None):
        # one of the lesser known and used/useful dict methods
        return cls(dict.fromkeys(keys, value))

    def xǁFrozenDictǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return f'{cn}({dict.__repr__(self)})'

    def xǁFrozenDictǁ__repr____mutmut_1(self):
        cn = None
        return f'{cn}({dict.__repr__(self)})'

    def xǁFrozenDictǁ__repr____mutmut_2(self):
        cn = self.__class__.__name__
        return f'{cn}({dict.__repr__(None)})'
    
    xǁFrozenDictǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFrozenDictǁ__repr____mutmut_1': xǁFrozenDictǁ__repr____mutmut_1, 
        'xǁFrozenDictǁ__repr____mutmut_2': xǁFrozenDictǁ__repr____mutmut_2
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFrozenDictǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁFrozenDictǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁFrozenDictǁ__repr____mutmut_orig)
    xǁFrozenDictǁ__repr____mutmut_orig.__name__ = 'xǁFrozenDictǁ__repr__'

    def xǁFrozenDictǁ__reduce_ex____mutmut_orig(self, protocol):
        return type(self), (dict(self),)

    def xǁFrozenDictǁ__reduce_ex____mutmut_1(self, protocol):
        return type(None), (dict(self),)

    def xǁFrozenDictǁ__reduce_ex____mutmut_2(self, protocol):
        return type(self), (dict(None),)
    
    xǁFrozenDictǁ__reduce_ex____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFrozenDictǁ__reduce_ex____mutmut_1': xǁFrozenDictǁ__reduce_ex____mutmut_1, 
        'xǁFrozenDictǁ__reduce_ex____mutmut_2': xǁFrozenDictǁ__reduce_ex____mutmut_2
    }
    
    def __reduce_ex__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFrozenDictǁ__reduce_ex____mutmut_orig"), object.__getattribute__(self, "xǁFrozenDictǁ__reduce_ex____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __reduce_ex__.__signature__ = _mutmut_signature(xǁFrozenDictǁ__reduce_ex____mutmut_orig)
    xǁFrozenDictǁ__reduce_ex____mutmut_orig.__name__ = 'xǁFrozenDictǁ__reduce_ex__'

    def xǁFrozenDictǁ__hash____mutmut_orig(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_1(self):
        try:
            ret = None
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_2(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = None
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_3(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(None)
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_4(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(None))
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_5(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = None

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_6(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = FrozenHashError(None)

        if ret.__class__ is FrozenHashError:
            raise ret

        return ret

    def xǁFrozenDictǁ__hash____mutmut_7(self):
        try:
            ret = self._hash
        except AttributeError:
            try:
                ret = self._hash = hash(frozenset(self.items()))
            except Exception as e:
                ret = self._hash = FrozenHashError(e)

        if ret.__class__ is not FrozenHashError:
            raise ret

        return ret
    
    xǁFrozenDictǁ__hash____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFrozenDictǁ__hash____mutmut_1': xǁFrozenDictǁ__hash____mutmut_1, 
        'xǁFrozenDictǁ__hash____mutmut_2': xǁFrozenDictǁ__hash____mutmut_2, 
        'xǁFrozenDictǁ__hash____mutmut_3': xǁFrozenDictǁ__hash____mutmut_3, 
        'xǁFrozenDictǁ__hash____mutmut_4': xǁFrozenDictǁ__hash____mutmut_4, 
        'xǁFrozenDictǁ__hash____mutmut_5': xǁFrozenDictǁ__hash____mutmut_5, 
        'xǁFrozenDictǁ__hash____mutmut_6': xǁFrozenDictǁ__hash____mutmut_6, 
        'xǁFrozenDictǁ__hash____mutmut_7': xǁFrozenDictǁ__hash____mutmut_7
    }
    
    def __hash__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFrozenDictǁ__hash____mutmut_orig"), object.__getattribute__(self, "xǁFrozenDictǁ__hash____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __hash__.__signature__ = _mutmut_signature(xǁFrozenDictǁ__hash____mutmut_orig)
    xǁFrozenDictǁ__hash____mutmut_orig.__name__ = 'xǁFrozenDictǁ__hash__'

    def __copy__(self):
        return self  # immutable types don't copy, see tuple's behavior

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_orig(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError('%s object is immutable' % self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_1(self, *a, **kw):
        "XXraises a TypeError, because FrozenDicts are immutableXX"
        raise TypeError('%s object is immutable' % self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_2(self, *a, **kw):
        "raises a typeerror, because frozendicts are immutable"
        raise TypeError('%s object is immutable' % self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_3(self, *a, **kw):
        "RAISES A TYPEERROR, BECAUSE FROZENDICTS ARE IMMUTABLE"
        raise TypeError('%s object is immutable' % self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_4(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError(None)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_5(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError('%s object is immutable' / self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_6(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError('XX%s object is immutableXX' % self.__class__.__name__)

    # block everything else
    def xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_7(self, *a, **kw):
        "raises a TypeError, because FrozenDicts are immutable"
        raise TypeError('%S OBJECT IS IMMUTABLE' % self.__class__.__name__)
    
    xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_1': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_1, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_2': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_2, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_3': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_3, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_4': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_4, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_5': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_5, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_6': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_6, 
        'xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_7': xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_7
    }
    
    def _raise_frozen_typeerror(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_orig"), object.__getattribute__(self, "xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _raise_frozen_typeerror.__signature__ = _mutmut_signature(xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_orig)
    xǁFrozenDictǁ_raise_frozen_typeerror__mutmut_orig.__name__ = 'xǁFrozenDictǁ_raise_frozen_typeerror'

    __ior__ = __setitem__ = __delitem__ = update = _raise_frozen_typeerror
    setdefault = pop = popitem = clear = _raise_frozen_typeerror

    del _raise_frozen_typeerror


# end dictutils.py
