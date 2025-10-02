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

"""Python comes with a many great data structures, from :class:`dict`
to :class:`collections.deque`, and no shortage of serviceable
algorithm implementations, from :func:`sorted` to :mod:`bisect`. But
priority queues are curiously relegated to an example documented in
:mod:`heapq`. Even there, the approach presented is not full-featured
and object-oriented. There is a built-in priority queue,
:class:`Queue.PriorityQueue`, but in addition to its austere API, it
carries the double-edged sword of threadsafety, making it fine for
multi-threaded, multi-consumer applications, but high-overhead for
cooperative/single-threaded use cases.

The ``queueutils`` module currently provides two Queue
implementations: :class:`HeapPriorityQueue`, based on a heap, and
:class:`SortedPriorityQueue`, based on a sorted list. Both use a
unified API based on :class:`BasePriorityQueue` to facilitate testing
the slightly different performance characteristics on various
application use cases.

>>> pq = PriorityQueue()
>>> pq.add('low priority task', 0)
>>> pq.add('high priority task', 2)
>>> pq.add('medium priority task 1', 1)
>>> pq.add('medium priority task 2', 1)
>>> len(pq)
4
>>> pq.pop()
'high priority task'
>>> pq.peek()
'medium priority task 1'
>>> len(pq)
3

"""


from heapq import heappush, heappop
from bisect import insort
import itertools

_REMOVED = object()

try:
    from .listutils import BList
    # see BarrelList docstring for notes
except ImportError:
    BList = list


__all__ = ['PriorityQueue', 'BasePriorityQueue',
           'HeapPriorityQueue', 'SortedPriorityQueue']
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


# TODO: make Base a real abstract class
# TODO: add uniqueification


class BasePriorityQueue:
    """The abstract base class for the other PriorityQueues in this
    module. Override the ``_backend_type`` class attribute, as well as
    the :meth:`_push_entry` and :meth:`_pop_entry` staticmethods for
    custom subclass behavior. (Don't forget to use
    :func:`staticmethod`).

    Args:
        priority_key (callable): A function that takes *priority* as
            passed in by :meth:`add` and returns a real number
            representing the effective priority.

    """
    # negating priority means larger numbers = higher priority
    _default_priority_key = staticmethod(lambda p: -float(p or 0))
    _backend_type = list

    def xǁBasePriorityQueueǁ__init____mutmut_orig(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_1(self, **kw):
        self._pq = None
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_2(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = None
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_3(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = None
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_4(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = None
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_5(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop(None, self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_6(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', None)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_7(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop(self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_8(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', )
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_9(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('XXpriority_keyXX', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_10(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('PRIORITY_KEY', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_11(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError(None)

    def xǁBasePriorityQueueǁ__init____mutmut_12(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' / kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_13(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('XXunexpected keyword arguments: %rXX' % kw.keys())

    def xǁBasePriorityQueueǁ__init____mutmut_14(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)
        if kw:
            raise TypeError('UNEXPECTED KEYWORD ARGUMENTS: %R' % kw.keys())
    
    xǁBasePriorityQueueǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁ__init____mutmut_1': xǁBasePriorityQueueǁ__init____mutmut_1, 
        'xǁBasePriorityQueueǁ__init____mutmut_2': xǁBasePriorityQueueǁ__init____mutmut_2, 
        'xǁBasePriorityQueueǁ__init____mutmut_3': xǁBasePriorityQueueǁ__init____mutmut_3, 
        'xǁBasePriorityQueueǁ__init____mutmut_4': xǁBasePriorityQueueǁ__init____mutmut_4, 
        'xǁBasePriorityQueueǁ__init____mutmut_5': xǁBasePriorityQueueǁ__init____mutmut_5, 
        'xǁBasePriorityQueueǁ__init____mutmut_6': xǁBasePriorityQueueǁ__init____mutmut_6, 
        'xǁBasePriorityQueueǁ__init____mutmut_7': xǁBasePriorityQueueǁ__init____mutmut_7, 
        'xǁBasePriorityQueueǁ__init____mutmut_8': xǁBasePriorityQueueǁ__init____mutmut_8, 
        'xǁBasePriorityQueueǁ__init____mutmut_9': xǁBasePriorityQueueǁ__init____mutmut_9, 
        'xǁBasePriorityQueueǁ__init____mutmut_10': xǁBasePriorityQueueǁ__init____mutmut_10, 
        'xǁBasePriorityQueueǁ__init____mutmut_11': xǁBasePriorityQueueǁ__init____mutmut_11, 
        'xǁBasePriorityQueueǁ__init____mutmut_12': xǁBasePriorityQueueǁ__init____mutmut_12, 
        'xǁBasePriorityQueueǁ__init____mutmut_13': xǁBasePriorityQueueǁ__init____mutmut_13, 
        'xǁBasePriorityQueueǁ__init____mutmut_14': xǁBasePriorityQueueǁ__init____mutmut_14
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁ__init____mutmut_orig)
    xǁBasePriorityQueueǁ__init____mutmut_orig.__name__ = 'xǁBasePriorityQueueǁ__init__'

    @staticmethod
    def _push_entry(backend, entry):
        pass  # abstract

    @staticmethod
    def _pop_entry(backend):
        pass  # abstract

    def xǁBasePriorityQueueǁadd__mutmut_orig(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_1(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = None
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_2(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(None)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_3(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task not in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_4(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(None)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_5(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = None
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_6(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(None)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_7(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = None
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_8(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = None
        self._push_entry(self._pq, entry)

    def xǁBasePriorityQueueǁadd__mutmut_9(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(None, entry)

    def xǁBasePriorityQueueǁadd__mutmut_10(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, None)

    def xǁBasePriorityQueueǁadd__mutmut_11(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(entry)

    def xǁBasePriorityQueueǁadd__mutmut_12(self, task, priority=None):
        """
        Add a task to the queue, or change the *task*'s priority if *task*
        is already in the queue. *task* can be any hashable object,
        and *priority* defaults to ``0``. Higher values representing
        higher priority, but this behavior can be controlled by
        setting *priority_key* in the constructor.
        """
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, )
    
    xǁBasePriorityQueueǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁadd__mutmut_1': xǁBasePriorityQueueǁadd__mutmut_1, 
        'xǁBasePriorityQueueǁadd__mutmut_2': xǁBasePriorityQueueǁadd__mutmut_2, 
        'xǁBasePriorityQueueǁadd__mutmut_3': xǁBasePriorityQueueǁadd__mutmut_3, 
        'xǁBasePriorityQueueǁadd__mutmut_4': xǁBasePriorityQueueǁadd__mutmut_4, 
        'xǁBasePriorityQueueǁadd__mutmut_5': xǁBasePriorityQueueǁadd__mutmut_5, 
        'xǁBasePriorityQueueǁadd__mutmut_6': xǁBasePriorityQueueǁadd__mutmut_6, 
        'xǁBasePriorityQueueǁadd__mutmut_7': xǁBasePriorityQueueǁadd__mutmut_7, 
        'xǁBasePriorityQueueǁadd__mutmut_8': xǁBasePriorityQueueǁadd__mutmut_8, 
        'xǁBasePriorityQueueǁadd__mutmut_9': xǁBasePriorityQueueǁadd__mutmut_9, 
        'xǁBasePriorityQueueǁadd__mutmut_10': xǁBasePriorityQueueǁadd__mutmut_10, 
        'xǁBasePriorityQueueǁadd__mutmut_11': xǁBasePriorityQueueǁadd__mutmut_11, 
        'xǁBasePriorityQueueǁadd__mutmut_12': xǁBasePriorityQueueǁadd__mutmut_12
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁadd__mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁadd__mutmut_orig)
    xǁBasePriorityQueueǁadd__mutmut_orig.__name__ = 'xǁBasePriorityQueueǁadd'

    def xǁBasePriorityQueueǁremove__mutmut_orig(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(task)
        entry[-1] = _REMOVED

    def xǁBasePriorityQueueǁremove__mutmut_1(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = None
        entry[-1] = _REMOVED

    def xǁBasePriorityQueueǁremove__mutmut_2(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(None)
        entry[-1] = _REMOVED

    def xǁBasePriorityQueueǁremove__mutmut_3(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(task)
        entry[-1] = None

    def xǁBasePriorityQueueǁremove__mutmut_4(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(task)
        entry[+1] = _REMOVED

    def xǁBasePriorityQueueǁremove__mutmut_5(self, task):
        """Remove a task from the priority queue. Raises :exc:`KeyError` if
        the *task* is absent.
        """
        entry = self._entry_map.pop(task)
        entry[-2] = _REMOVED
    
    xǁBasePriorityQueueǁremove__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁremove__mutmut_1': xǁBasePriorityQueueǁremove__mutmut_1, 
        'xǁBasePriorityQueueǁremove__mutmut_2': xǁBasePriorityQueueǁremove__mutmut_2, 
        'xǁBasePriorityQueueǁremove__mutmut_3': xǁBasePriorityQueueǁremove__mutmut_3, 
        'xǁBasePriorityQueueǁremove__mutmut_4': xǁBasePriorityQueueǁremove__mutmut_4, 
        'xǁBasePriorityQueueǁremove__mutmut_5': xǁBasePriorityQueueǁremove__mutmut_5
    }
    
    def remove(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁremove__mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁremove__mutmut_mutants"), args, kwargs, self)
        return result 
    
    remove.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁremove__mutmut_orig)
    xǁBasePriorityQueueǁremove__mutmut_orig.__name__ = 'xǁBasePriorityQueueǁremove'

    def xǁBasePriorityQueueǁ_cull__mutmut_orig(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_1(self, raise_exc=False):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_2(self, raise_exc=True):
        "XXRemove entries marked as removed by previous :meth:`remove` calls.XX"
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_3(self, raise_exc=True):
        "remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_4(self, raise_exc=True):
        "REMOVE ENTRIES MARKED AS REMOVED BY PREVIOUS :METH:`REMOVE` CALLS."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_5(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = None
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_6(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[1]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_7(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is not _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_8(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(None)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_9(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                break
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def xǁBasePriorityQueueǁ_cull__mutmut_10(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError(None)

    def xǁBasePriorityQueueǁ_cull__mutmut_11(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('XXempty priority queueXX')

    def xǁBasePriorityQueueǁ_cull__mutmut_12(self, raise_exc=True):
        "Remove entries marked as removed by previous :meth:`remove` calls."
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('EMPTY PRIORITY QUEUE')
    
    xǁBasePriorityQueueǁ_cull__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁ_cull__mutmut_1': xǁBasePriorityQueueǁ_cull__mutmut_1, 
        'xǁBasePriorityQueueǁ_cull__mutmut_2': xǁBasePriorityQueueǁ_cull__mutmut_2, 
        'xǁBasePriorityQueueǁ_cull__mutmut_3': xǁBasePriorityQueueǁ_cull__mutmut_3, 
        'xǁBasePriorityQueueǁ_cull__mutmut_4': xǁBasePriorityQueueǁ_cull__mutmut_4, 
        'xǁBasePriorityQueueǁ_cull__mutmut_5': xǁBasePriorityQueueǁ_cull__mutmut_5, 
        'xǁBasePriorityQueueǁ_cull__mutmut_6': xǁBasePriorityQueueǁ_cull__mutmut_6, 
        'xǁBasePriorityQueueǁ_cull__mutmut_7': xǁBasePriorityQueueǁ_cull__mutmut_7, 
        'xǁBasePriorityQueueǁ_cull__mutmut_8': xǁBasePriorityQueueǁ_cull__mutmut_8, 
        'xǁBasePriorityQueueǁ_cull__mutmut_9': xǁBasePriorityQueueǁ_cull__mutmut_9, 
        'xǁBasePriorityQueueǁ_cull__mutmut_10': xǁBasePriorityQueueǁ_cull__mutmut_10, 
        'xǁBasePriorityQueueǁ_cull__mutmut_11': xǁBasePriorityQueueǁ_cull__mutmut_11, 
        'xǁBasePriorityQueueǁ_cull__mutmut_12': xǁBasePriorityQueueǁ_cull__mutmut_12
    }
    
    def _cull(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁ_cull__mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁ_cull__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cull.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁ_cull__mutmut_orig)
    xǁBasePriorityQueueǁ_cull__mutmut_orig.__name__ = 'xǁBasePriorityQueueǁ_cull'

    def xǁBasePriorityQueueǁpeek__mutmut_orig(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_1(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = None
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_2(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[1]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_3(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_4(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError(None)
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_5(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('XXpeek on empty queueXX')
        return task

    def xǁBasePriorityQueueǁpeek__mutmut_6(self, default=_REMOVED):
        """Read the next value in the queue without removing it. Returns
        *default* on an empty queue, or raises :exc:`KeyError` if
        *default* is not set.
        """
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('PEEK ON EMPTY QUEUE')
        return task
    
    xǁBasePriorityQueueǁpeek__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁpeek__mutmut_1': xǁBasePriorityQueueǁpeek__mutmut_1, 
        'xǁBasePriorityQueueǁpeek__mutmut_2': xǁBasePriorityQueueǁpeek__mutmut_2, 
        'xǁBasePriorityQueueǁpeek__mutmut_3': xǁBasePriorityQueueǁpeek__mutmut_3, 
        'xǁBasePriorityQueueǁpeek__mutmut_4': xǁBasePriorityQueueǁpeek__mutmut_4, 
        'xǁBasePriorityQueueǁpeek__mutmut_5': xǁBasePriorityQueueǁpeek__mutmut_5, 
        'xǁBasePriorityQueueǁpeek__mutmut_6': xǁBasePriorityQueueǁpeek__mutmut_6
    }
    
    def peek(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁpeek__mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁpeek__mutmut_mutants"), args, kwargs, self)
        return result 
    
    peek.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁpeek__mutmut_orig)
    xǁBasePriorityQueueǁpeek__mutmut_orig.__name__ = 'xǁBasePriorityQueueǁpeek'

    def xǁBasePriorityQueueǁpop__mutmut_orig(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def xǁBasePriorityQueueǁpop__mutmut_1(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = None
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def xǁBasePriorityQueueǁpop__mutmut_2(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(None)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def xǁBasePriorityQueueǁpop__mutmut_3(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def xǁBasePriorityQueueǁpop__mutmut_4(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError(None)
        return task

    def xǁBasePriorityQueueǁpop__mutmut_5(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('XXpop on empty queueXX')
        return task

    def xǁBasePriorityQueueǁpop__mutmut_6(self, default=_REMOVED):
        """Remove and return the next value in the queue. Returns *default* on
        an empty queue, or raises :exc:`KeyError` if *default* is not
        set.
        """
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('POP ON EMPTY QUEUE')
        return task
    
    xǁBasePriorityQueueǁpop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁpop__mutmut_1': xǁBasePriorityQueueǁpop__mutmut_1, 
        'xǁBasePriorityQueueǁpop__mutmut_2': xǁBasePriorityQueueǁpop__mutmut_2, 
        'xǁBasePriorityQueueǁpop__mutmut_3': xǁBasePriorityQueueǁpop__mutmut_3, 
        'xǁBasePriorityQueueǁpop__mutmut_4': xǁBasePriorityQueueǁpop__mutmut_4, 
        'xǁBasePriorityQueueǁpop__mutmut_5': xǁBasePriorityQueueǁpop__mutmut_5, 
        'xǁBasePriorityQueueǁpop__mutmut_6': xǁBasePriorityQueueǁpop__mutmut_6
    }
    
    def pop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁpop__mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁpop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    pop.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁpop__mutmut_orig)
    xǁBasePriorityQueueǁpop__mutmut_orig.__name__ = 'xǁBasePriorityQueueǁpop'

    def xǁBasePriorityQueueǁ__len____mutmut_orig(self):
        "Return the number of tasks in the queue."
        return len(self._entry_map)

    def xǁBasePriorityQueueǁ__len____mutmut_1(self):
        "XXReturn the number of tasks in the queue.XX"
        return len(self._entry_map)

    def xǁBasePriorityQueueǁ__len____mutmut_2(self):
        "return the number of tasks in the queue."
        return len(self._entry_map)

    def xǁBasePriorityQueueǁ__len____mutmut_3(self):
        "RETURN THE NUMBER OF TASKS IN THE QUEUE."
        return len(self._entry_map)
    
    xǁBasePriorityQueueǁ__len____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBasePriorityQueueǁ__len____mutmut_1': xǁBasePriorityQueueǁ__len____mutmut_1, 
        'xǁBasePriorityQueueǁ__len____mutmut_2': xǁBasePriorityQueueǁ__len____mutmut_2, 
        'xǁBasePriorityQueueǁ__len____mutmut_3': xǁBasePriorityQueueǁ__len____mutmut_3
    }
    
    def __len__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBasePriorityQueueǁ__len____mutmut_orig"), object.__getattribute__(self, "xǁBasePriorityQueueǁ__len____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __len__.__signature__ = _mutmut_signature(xǁBasePriorityQueueǁ__len____mutmut_orig)
    xǁBasePriorityQueueǁ__len____mutmut_orig.__name__ = 'xǁBasePriorityQueueǁ__len__'


class HeapPriorityQueue(BasePriorityQueue):
    """A priority queue inherited from :class:`BasePriorityQueue`,
    backed by a list and based on the :func:`heapq.heappop` and
    :func:`heapq.heappush` functions in the built-in :mod:`heapq`
    module.
    """
    @staticmethod
    def _pop_entry(backend):
        return heappop(backend)

    @staticmethod
    def _push_entry(backend, entry):
        heappush(backend, entry)


class SortedPriorityQueue(BasePriorityQueue):
    """A priority queue inherited from :class:`BasePriorityQueue`, based
    on the :func:`bisect.insort` approach for in-order insertion into
    a sorted list.
    """
    _backend_type = BList

    @staticmethod
    def _pop_entry(backend):
        return backend.pop(0)

    @staticmethod
    def _push_entry(backend, entry):
        insort(backend, entry)


PriorityQueue = SortedPriorityQueue
