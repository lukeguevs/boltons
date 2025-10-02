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

"""The Python Garbage Collector (`GC`_) doesn't usually get too much
attention, probably because:

  - Python's `reference counting`_ effectively handles the vast majority of
    unused objects
  - People are slowly learning to avoid implementing `object.__del__()`_
  - The collection itself strikes a good balance between simplicity and
    power (`tunable generation sizes`_)
  - The collector itself is fast and rarely the cause of long pauses
    associated with GC in other runtimes

Even so, for many applications, the time will come when the developer
will need to track down:

  - Circular references
  - Misbehaving objects (locks, ``__del__()``)
  - Memory leaks
  - Or just ways to shave off a couple percent of execution time

Thanks to the :mod:`gc` module, the GC is a well-instrumented entry
point for exactly these tasks, and ``gcutils`` aims to facilitate it
further.

.. _GC: https://docs.python.org/2/glossary.html#term-garbage-collection
.. _reference counting: https://docs.python.org/2/glossary.html#term-reference-count
.. _object.__del__(): https://docs.python.org/2/glossary.html#term-reference-count
.. _tunable generation sizes: https://docs.python.org/2/library/gc.html#gc.set_threshold
"""
# TODO: type survey


import gc
import sys

__all__ = ['get_all', 'GCToggler', 'toggle_gc', 'toggle_gc_postcollect']
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


def x_get_all__mutmut_orig(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_1(type_obj, include_subtypes=False):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_2(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_3(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError(None)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_4(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' / type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_5(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('XXexpected a type, not %rXX' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_6(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('EXPECTED A TYPE, NOT %R' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_7(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = None
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_8(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(None)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_9(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = None  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_10(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = True  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_11(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = None
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_12(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(None)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_13(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = None

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_14(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = None
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


def x_get_all__mutmut_15(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = None
    return ret


def x_get_all__mutmut_16(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(None) is type_obj]
    return ret


def x_get_all__mutmut_17(type_obj, include_subtypes=True):
    """Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referents`.

    ``get_all()`` is optimized such that getting instances of
    user-created types is quite fast. Setting *include_subtypes* to
    ``False`` will further increase performance in cases where
    instances of subtypes aren't required.

    .. note::

      There are no guarantees about the state of objects returned by
      ``get_all()``, especially in concurrent environments. For
      instance, it is possible for an object to be in the middle of
      executing its ``__init__()`` and be only partially constructed.
    """
    # TODO: old-style classes
    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    try:
        type_is_tracked = gc.is_tracked(type_obj)
    except AttributeError:
        type_is_tracked = False  # Python 2.6 and below don't get the speedup
    if type_is_tracked:
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is not type_obj]
    return ret

x_get_all__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_all__mutmut_1': x_get_all__mutmut_1, 
    'x_get_all__mutmut_2': x_get_all__mutmut_2, 
    'x_get_all__mutmut_3': x_get_all__mutmut_3, 
    'x_get_all__mutmut_4': x_get_all__mutmut_4, 
    'x_get_all__mutmut_5': x_get_all__mutmut_5, 
    'x_get_all__mutmut_6': x_get_all__mutmut_6, 
    'x_get_all__mutmut_7': x_get_all__mutmut_7, 
    'x_get_all__mutmut_8': x_get_all__mutmut_8, 
    'x_get_all__mutmut_9': x_get_all__mutmut_9, 
    'x_get_all__mutmut_10': x_get_all__mutmut_10, 
    'x_get_all__mutmut_11': x_get_all__mutmut_11, 
    'x_get_all__mutmut_12': x_get_all__mutmut_12, 
    'x_get_all__mutmut_13': x_get_all__mutmut_13, 
    'x_get_all__mutmut_14': x_get_all__mutmut_14, 
    'x_get_all__mutmut_15': x_get_all__mutmut_15, 
    'x_get_all__mutmut_16': x_get_all__mutmut_16, 
    'x_get_all__mutmut_17': x_get_all__mutmut_17
}

def get_all(*args, **kwargs):
    result = _mutmut_trampoline(x_get_all__mutmut_orig, x_get_all__mutmut_mutants, args, kwargs)
    return result 

get_all.__signature__ = _mutmut_signature(x_get_all__mutmut_orig)
x_get_all__mutmut_orig.__name__ = 'x_get_all'


_IS_PYPY = '__pypy__' in sys.builtin_module_names
if _IS_PYPY:
    # pypy's gc is just different, y'all
    del get_all


class GCToggler:
    """The ``GCToggler`` is a context-manager that allows one to safely
    take more control of your garbage collection schedule. Anecdotal
    experience says certain object-creation-heavy tasks see speedups
    of around 10% by simply doing one explicit collection at the very
    end, especially if most of the objects will stay resident.

    Two GCTogglers are already present in the ``gcutils`` module:

    - :data:`toggle_gc` simply turns off GC at context entrance, and
      re-enables at exit
    - :data:`toggle_gc_postcollect` does the same, but triggers an
      explicit collection after re-enabling.

    >>> with toggle_gc:
    ...     x = [object() for i in range(1000)]

    Between those two instances, the ``GCToggler`` type probably won't
    be used much directly, but is documented for inheritance purposes.
    """
    def xǁGCTogglerǁ__init____mutmut_orig(self, postcollect=False):
        self.postcollect = postcollect
    def xǁGCTogglerǁ__init____mutmut_1(self, postcollect=True):
        self.postcollect = postcollect
    def xǁGCTogglerǁ__init____mutmut_2(self, postcollect=False):
        self.postcollect = None
    
    xǁGCTogglerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGCTogglerǁ__init____mutmut_1': xǁGCTogglerǁ__init____mutmut_1, 
        'xǁGCTogglerǁ__init____mutmut_2': xǁGCTogglerǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGCTogglerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁGCTogglerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁGCTogglerǁ__init____mutmut_orig)
    xǁGCTogglerǁ__init____mutmut_orig.__name__ = 'xǁGCTogglerǁ__init__'

    def __enter__(self):
        gc.disable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.enable()
        if self.postcollect:
            gc.collect()


toggle_gc = GCToggler()
"""A context manager for disabling GC for a code block. See
:class:`GCToggler` for more details."""


toggle_gc_postcollect = GCToggler(postcollect=True)
"""A context manager for disabling GC for a code block, and collecting
before re-enabling. See :class:`GCToggler` for more details."""
