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

"""This module provides useful math functions on top of Python's
built-in :mod:`math` module.
"""

from math import ceil as _ceil, floor as _floor
import bisect
import binascii
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


def x_clamp__mutmut_orig(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, lower), upper)


def x_clamp__mutmut_1(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper <= lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, lower), upper)


def x_clamp__mutmut_2(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError(None)
    return min(max(x, lower), upper)


def x_clamp__mutmut_3(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)' / (upper, lower))
    return min(max(x, lower), upper)


def x_clamp__mutmut_4(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('XXexpected upper bound (%r) >= lower bound (%r)XX'
                         % (upper, lower))
    return min(max(x, lower), upper)


def x_clamp__mutmut_5(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('EXPECTED UPPER BOUND (%R) >= LOWER BOUND (%R)'
                         % (upper, lower))
    return min(max(x, lower), upper)


def x_clamp__mutmut_6(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(None, upper)


def x_clamp__mutmut_7(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, lower), None)


def x_clamp__mutmut_8(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(upper)


def x_clamp__mutmut_9(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, lower), )


def x_clamp__mutmut_10(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(None, lower), upper)


def x_clamp__mutmut_11(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, None), upper)


def x_clamp__mutmut_12(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(lower), upper)


def x_clamp__mutmut_13(x, lower=float('-inf'), upper=float('inf')):
    """Limit a value to a given range.

    Args:
        x (int or float): Number to be clamped.
        lower (int or float): Minimum value for x.
        upper (int or float): Maximum value for x.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    >>> clamp(1.0, 0, 5)
    1.0
    >>> clamp(-1.0, 0, 5)
    0
    >>> clamp(101.0, 0, 5)
    5
    >>> clamp(123, upper=5)
    5

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html

    """
    if upper < lower:
        raise ValueError('expected upper bound (%r) >= lower bound (%r)'
                         % (upper, lower))
    return min(max(x, ), upper)

x_clamp__mutmut_mutants : ClassVar[MutantDict] = {
'x_clamp__mutmut_1': x_clamp__mutmut_1, 
    'x_clamp__mutmut_2': x_clamp__mutmut_2, 
    'x_clamp__mutmut_3': x_clamp__mutmut_3, 
    'x_clamp__mutmut_4': x_clamp__mutmut_4, 
    'x_clamp__mutmut_5': x_clamp__mutmut_5, 
    'x_clamp__mutmut_6': x_clamp__mutmut_6, 
    'x_clamp__mutmut_7': x_clamp__mutmut_7, 
    'x_clamp__mutmut_8': x_clamp__mutmut_8, 
    'x_clamp__mutmut_9': x_clamp__mutmut_9, 
    'x_clamp__mutmut_10': x_clamp__mutmut_10, 
    'x_clamp__mutmut_11': x_clamp__mutmut_11, 
    'x_clamp__mutmut_12': x_clamp__mutmut_12, 
    'x_clamp__mutmut_13': x_clamp__mutmut_13
}

def clamp(*args, **kwargs):
    result = _mutmut_trampoline(x_clamp__mutmut_orig, x_clamp__mutmut_mutants, args, kwargs)
    return result 

clamp.__signature__ = _mutmut_signature(x_clamp__mutmut_orig)
x_clamp__mutmut_orig.__name__ = 'x_clamp'


def x_ceil__mutmut_orig(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_1(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is not None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_2(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(None)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_3(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = None
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_4(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(None)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_5(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = None
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_6(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(None, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_7(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, None)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_8(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_9(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, )
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_10(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i != len(options):
        raise ValueError("no ceil options greater than or equal to: %r" % x)
    return options[i]


def x_ceil__mutmut_11(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError(None)
    return options[i]


def x_ceil__mutmut_12(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("no ceil options greater than or equal to: %r" / x)
    return options[i]


def x_ceil__mutmut_13(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("XXno ceil options greater than or equal to: %rXX" % x)
    return options[i]


def x_ceil__mutmut_14(x, options=None):
    """Return the ceiling of *x*. If *options* is set, return the smallest
    integer or float from *options* that is greater than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil(3.5, options=VALID_CABLE_CSA)
    4
    >>> ceil(4, options=VALID_CABLE_CSA)
    4
    """
    if options is None:
        return _ceil(x)
    options = sorted(options)
    i = bisect.bisect_left(options, x)
    if i == len(options):
        raise ValueError("NO CEIL OPTIONS GREATER THAN OR EQUAL TO: %R" % x)
    return options[i]

x_ceil__mutmut_mutants : ClassVar[MutantDict] = {
'x_ceil__mutmut_1': x_ceil__mutmut_1, 
    'x_ceil__mutmut_2': x_ceil__mutmut_2, 
    'x_ceil__mutmut_3': x_ceil__mutmut_3, 
    'x_ceil__mutmut_4': x_ceil__mutmut_4, 
    'x_ceil__mutmut_5': x_ceil__mutmut_5, 
    'x_ceil__mutmut_6': x_ceil__mutmut_6, 
    'x_ceil__mutmut_7': x_ceil__mutmut_7, 
    'x_ceil__mutmut_8': x_ceil__mutmut_8, 
    'x_ceil__mutmut_9': x_ceil__mutmut_9, 
    'x_ceil__mutmut_10': x_ceil__mutmut_10, 
    'x_ceil__mutmut_11': x_ceil__mutmut_11, 
    'x_ceil__mutmut_12': x_ceil__mutmut_12, 
    'x_ceil__mutmut_13': x_ceil__mutmut_13, 
    'x_ceil__mutmut_14': x_ceil__mutmut_14
}

def ceil(*args, **kwargs):
    result = _mutmut_trampoline(x_ceil__mutmut_orig, x_ceil__mutmut_mutants, args, kwargs)
    return result 

ceil.__signature__ = _mutmut_signature(x_ceil__mutmut_orig)
x_ceil__mutmut_orig.__name__ = 'x_ceil'


def x_floor__mutmut_orig(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_1(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is not None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_2(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(None)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_3(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = None

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_4(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(None)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_5(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = None
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_6(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(None, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_7(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, None)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_8(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_9(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, )
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_10(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 1]


def x_floor__mutmut_11(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError(None)
    return options[i - 1]


def x_floor__mutmut_12(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" / x)
    return options[i - 1]


def x_floor__mutmut_13(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("XXno floor options less than or equal to: %rXX" % x)
    return options[i - 1]


def x_floor__mutmut_14(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("NO FLOOR OPTIONS LESS THAN OR EQUAL TO: %R" % x)
    return options[i - 1]


def x_floor__mutmut_15(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i + 1]


def x_floor__mutmut_16(x, options=None):
    """Return the floor of *x*. If *options* is set, return the largest
    integer or float from *options* that is less than or equal to
    *x*.

    Args:
        x (int or float): Number to be tested.
        options (iterable): Optional iterable of arbitrary numbers
          (ints or floats).

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor(3.5, options=VALID_CABLE_CSA)
    2.5
    >>> floor(2.5, options=VALID_CABLE_CSA)
    2.5

    """
    if options is None:
        return _floor(x)
    options = sorted(options)

    i = bisect.bisect_right(options, x)
    if not i:
        raise ValueError("no floor options less than or equal to: %r" % x)
    return options[i - 2]

x_floor__mutmut_mutants : ClassVar[MutantDict] = {
'x_floor__mutmut_1': x_floor__mutmut_1, 
    'x_floor__mutmut_2': x_floor__mutmut_2, 
    'x_floor__mutmut_3': x_floor__mutmut_3, 
    'x_floor__mutmut_4': x_floor__mutmut_4, 
    'x_floor__mutmut_5': x_floor__mutmut_5, 
    'x_floor__mutmut_6': x_floor__mutmut_6, 
    'x_floor__mutmut_7': x_floor__mutmut_7, 
    'x_floor__mutmut_8': x_floor__mutmut_8, 
    'x_floor__mutmut_9': x_floor__mutmut_9, 
    'x_floor__mutmut_10': x_floor__mutmut_10, 
    'x_floor__mutmut_11': x_floor__mutmut_11, 
    'x_floor__mutmut_12': x_floor__mutmut_12, 
    'x_floor__mutmut_13': x_floor__mutmut_13, 
    'x_floor__mutmut_14': x_floor__mutmut_14, 
    'x_floor__mutmut_15': x_floor__mutmut_15, 
    'x_floor__mutmut_16': x_floor__mutmut_16
}

def floor(*args, **kwargs):
    result = _mutmut_trampoline(x_floor__mutmut_orig, x_floor__mutmut_mutants, args, kwargs)
    return result 

floor.__signature__ = _mutmut_signature(x_floor__mutmut_orig)
x_floor__mutmut_orig.__name__ = 'x_floor'


class Bits:
    '''
    An immutable bit-string or bit-array object.
    Provides list-like access to bits as bools,
    as well as bitwise masking and shifting operators.
    Bits also make it easy to convert between many
    different useful representations:

    * bytes -- good for serializing raw binary data
    * int -- good for incrementing (e.g. to try all possible values)
    * list of bools -- good for iterating over or treating as flags
    * hex/bin string -- good for human readability

    '''
    __slots__ = ('val', 'len')

    def xǁBitsǁ__init____mutmut_orig(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_1(self, val=1, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_2(self, val=0, len_=None):
        if type(None) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_3(self, val=0, len_=None):
        if type(val) is int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_4(self, val=0, len_=None):
        if type(val) is not int:
            if type(None) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_5(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is not list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_6(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = None
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_7(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(None)
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_8(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = 'XXXX'.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_9(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['XX1XX' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_10(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else 'XX0XX' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_11(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(None) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_12(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is not bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_13(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = None
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_14(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode(None)
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_15(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('XXasciiXX')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_16(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ASCII')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_17(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(None) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_18(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is not str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_19(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is not None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_20(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = None
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_21(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith(None):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_22(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('XX0xXX'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_23(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0X'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_24(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = None
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_25(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) / 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_26(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ + 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_27(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 3) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_28(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 5
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_29(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith(None):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_30(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('XX0xXX'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_31(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0X'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_32(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = None
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_33(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(None, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_34(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, None)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_35(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_36(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, )
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_37(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 17)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_38(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = None
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_39(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(None, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_40(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, None)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_41(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_42(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, )
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_43(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 3)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_44(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = None
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_45(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 1
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_46(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(None) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_47(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_48(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(None)
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_49(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(None).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_50(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val <= 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_51(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 1:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_52(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError(None)
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_53(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('XXBits cannot represent negative valuesXX')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_54(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_55(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('BITS CANNOT REPRESENT NEGATIVE VALUES')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_56(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is not None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_57(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = None
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_58(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val >= 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_59(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 * len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_60(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 3 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_61(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(None)
        self.val = val  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_62(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = None  # data is stored internally as integer
        self.len = len_

    def xǁBitsǁ__init____mutmut_63(self, val=0, len_=None):
        if type(val) is not int:
            if type(val) is list:
                val = ''.join(['1' if e else '0' for e in val])
            if type(val) is bytes:
                val = val.decode('ascii')
            if type(val) is str:
                if len_ is None:
                    len_ = len(val)
                    if val.startswith('0x'):
                        len_ = (len_ - 2) * 4
                if val.startswith('0x'):
                    val = int(val, 16)
                else:
                    if val:
                        val = int(val, 2)
                    else:
                        val = 0
            if type(val) is not int:
                raise TypeError(f'initialized with bad type: {type(val).__name__}')
        if val < 0:
            raise ValueError('Bits cannot represent negative values')
        if len_ is None:
            len_ = len(f'{val:b}')
        if val > 2 ** len_:
            raise ValueError(f'value {val} cannot be represented with {len_} bits')
        self.val = val  # data is stored internally as integer
        self.len = None
    
    xǁBitsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__init____mutmut_1': xǁBitsǁ__init____mutmut_1, 
        'xǁBitsǁ__init____mutmut_2': xǁBitsǁ__init____mutmut_2, 
        'xǁBitsǁ__init____mutmut_3': xǁBitsǁ__init____mutmut_3, 
        'xǁBitsǁ__init____mutmut_4': xǁBitsǁ__init____mutmut_4, 
        'xǁBitsǁ__init____mutmut_5': xǁBitsǁ__init____mutmut_5, 
        'xǁBitsǁ__init____mutmut_6': xǁBitsǁ__init____mutmut_6, 
        'xǁBitsǁ__init____mutmut_7': xǁBitsǁ__init____mutmut_7, 
        'xǁBitsǁ__init____mutmut_8': xǁBitsǁ__init____mutmut_8, 
        'xǁBitsǁ__init____mutmut_9': xǁBitsǁ__init____mutmut_9, 
        'xǁBitsǁ__init____mutmut_10': xǁBitsǁ__init____mutmut_10, 
        'xǁBitsǁ__init____mutmut_11': xǁBitsǁ__init____mutmut_11, 
        'xǁBitsǁ__init____mutmut_12': xǁBitsǁ__init____mutmut_12, 
        'xǁBitsǁ__init____mutmut_13': xǁBitsǁ__init____mutmut_13, 
        'xǁBitsǁ__init____mutmut_14': xǁBitsǁ__init____mutmut_14, 
        'xǁBitsǁ__init____mutmut_15': xǁBitsǁ__init____mutmut_15, 
        'xǁBitsǁ__init____mutmut_16': xǁBitsǁ__init____mutmut_16, 
        'xǁBitsǁ__init____mutmut_17': xǁBitsǁ__init____mutmut_17, 
        'xǁBitsǁ__init____mutmut_18': xǁBitsǁ__init____mutmut_18, 
        'xǁBitsǁ__init____mutmut_19': xǁBitsǁ__init____mutmut_19, 
        'xǁBitsǁ__init____mutmut_20': xǁBitsǁ__init____mutmut_20, 
        'xǁBitsǁ__init____mutmut_21': xǁBitsǁ__init____mutmut_21, 
        'xǁBitsǁ__init____mutmut_22': xǁBitsǁ__init____mutmut_22, 
        'xǁBitsǁ__init____mutmut_23': xǁBitsǁ__init____mutmut_23, 
        'xǁBitsǁ__init____mutmut_24': xǁBitsǁ__init____mutmut_24, 
        'xǁBitsǁ__init____mutmut_25': xǁBitsǁ__init____mutmut_25, 
        'xǁBitsǁ__init____mutmut_26': xǁBitsǁ__init____mutmut_26, 
        'xǁBitsǁ__init____mutmut_27': xǁBitsǁ__init____mutmut_27, 
        'xǁBitsǁ__init____mutmut_28': xǁBitsǁ__init____mutmut_28, 
        'xǁBitsǁ__init____mutmut_29': xǁBitsǁ__init____mutmut_29, 
        'xǁBitsǁ__init____mutmut_30': xǁBitsǁ__init____mutmut_30, 
        'xǁBitsǁ__init____mutmut_31': xǁBitsǁ__init____mutmut_31, 
        'xǁBitsǁ__init____mutmut_32': xǁBitsǁ__init____mutmut_32, 
        'xǁBitsǁ__init____mutmut_33': xǁBitsǁ__init____mutmut_33, 
        'xǁBitsǁ__init____mutmut_34': xǁBitsǁ__init____mutmut_34, 
        'xǁBitsǁ__init____mutmut_35': xǁBitsǁ__init____mutmut_35, 
        'xǁBitsǁ__init____mutmut_36': xǁBitsǁ__init____mutmut_36, 
        'xǁBitsǁ__init____mutmut_37': xǁBitsǁ__init____mutmut_37, 
        'xǁBitsǁ__init____mutmut_38': xǁBitsǁ__init____mutmut_38, 
        'xǁBitsǁ__init____mutmut_39': xǁBitsǁ__init____mutmut_39, 
        'xǁBitsǁ__init____mutmut_40': xǁBitsǁ__init____mutmut_40, 
        'xǁBitsǁ__init____mutmut_41': xǁBitsǁ__init____mutmut_41, 
        'xǁBitsǁ__init____mutmut_42': xǁBitsǁ__init____mutmut_42, 
        'xǁBitsǁ__init____mutmut_43': xǁBitsǁ__init____mutmut_43, 
        'xǁBitsǁ__init____mutmut_44': xǁBitsǁ__init____mutmut_44, 
        'xǁBitsǁ__init____mutmut_45': xǁBitsǁ__init____mutmut_45, 
        'xǁBitsǁ__init____mutmut_46': xǁBitsǁ__init____mutmut_46, 
        'xǁBitsǁ__init____mutmut_47': xǁBitsǁ__init____mutmut_47, 
        'xǁBitsǁ__init____mutmut_48': xǁBitsǁ__init____mutmut_48, 
        'xǁBitsǁ__init____mutmut_49': xǁBitsǁ__init____mutmut_49, 
        'xǁBitsǁ__init____mutmut_50': xǁBitsǁ__init____mutmut_50, 
        'xǁBitsǁ__init____mutmut_51': xǁBitsǁ__init____mutmut_51, 
        'xǁBitsǁ__init____mutmut_52': xǁBitsǁ__init____mutmut_52, 
        'xǁBitsǁ__init____mutmut_53': xǁBitsǁ__init____mutmut_53, 
        'xǁBitsǁ__init____mutmut_54': xǁBitsǁ__init____mutmut_54, 
        'xǁBitsǁ__init____mutmut_55': xǁBitsǁ__init____mutmut_55, 
        'xǁBitsǁ__init____mutmut_56': xǁBitsǁ__init____mutmut_56, 
        'xǁBitsǁ__init____mutmut_57': xǁBitsǁ__init____mutmut_57, 
        'xǁBitsǁ__init____mutmut_58': xǁBitsǁ__init____mutmut_58, 
        'xǁBitsǁ__init____mutmut_59': xǁBitsǁ__init____mutmut_59, 
        'xǁBitsǁ__init____mutmut_60': xǁBitsǁ__init____mutmut_60, 
        'xǁBitsǁ__init____mutmut_61': xǁBitsǁ__init____mutmut_61, 
        'xǁBitsǁ__init____mutmut_62': xǁBitsǁ__init____mutmut_62, 
        'xǁBitsǁ__init____mutmut_63': xǁBitsǁ__init____mutmut_63
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBitsǁ__init____mutmut_orig)
    xǁBitsǁ__init____mutmut_orig.__name__ = 'xǁBitsǁ__init__'

    def xǁBitsǁ__getitem____mutmut_orig(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_1(self, k):
        if type(None) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_2(self, k):
        if type(k) is not slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_3(self, k):
        if type(k) is slice:
            return Bits(None)
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_4(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(None) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_5(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is not int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_6(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k > self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_7(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(None)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_8(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool(None)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_9(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) | self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_10(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 >> (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_11(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((2 << (self.len - k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_12(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k + 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_13(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len + k - 1)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_14(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 2)) & self.val)
        raise TypeError(type(k))

    def xǁBitsǁ__getitem____mutmut_15(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(None)

    def xǁBitsǁ__getitem____mutmut_16(self, k):
        if type(k) is slice:
            return Bits(self.as_bin()[k])
        if type(k) is int:
            if k >= self.len:
                raise IndexError(k)
            return bool((1 << (self.len - k - 1)) & self.val)
        raise TypeError(type(None))
    
    xǁBitsǁ__getitem____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__getitem____mutmut_1': xǁBitsǁ__getitem____mutmut_1, 
        'xǁBitsǁ__getitem____mutmut_2': xǁBitsǁ__getitem____mutmut_2, 
        'xǁBitsǁ__getitem____mutmut_3': xǁBitsǁ__getitem____mutmut_3, 
        'xǁBitsǁ__getitem____mutmut_4': xǁBitsǁ__getitem____mutmut_4, 
        'xǁBitsǁ__getitem____mutmut_5': xǁBitsǁ__getitem____mutmut_5, 
        'xǁBitsǁ__getitem____mutmut_6': xǁBitsǁ__getitem____mutmut_6, 
        'xǁBitsǁ__getitem____mutmut_7': xǁBitsǁ__getitem____mutmut_7, 
        'xǁBitsǁ__getitem____mutmut_8': xǁBitsǁ__getitem____mutmut_8, 
        'xǁBitsǁ__getitem____mutmut_9': xǁBitsǁ__getitem____mutmut_9, 
        'xǁBitsǁ__getitem____mutmut_10': xǁBitsǁ__getitem____mutmut_10, 
        'xǁBitsǁ__getitem____mutmut_11': xǁBitsǁ__getitem____mutmut_11, 
        'xǁBitsǁ__getitem____mutmut_12': xǁBitsǁ__getitem____mutmut_12, 
        'xǁBitsǁ__getitem____mutmut_13': xǁBitsǁ__getitem____mutmut_13, 
        'xǁBitsǁ__getitem____mutmut_14': xǁBitsǁ__getitem____mutmut_14, 
        'xǁBitsǁ__getitem____mutmut_15': xǁBitsǁ__getitem____mutmut_15, 
        'xǁBitsǁ__getitem____mutmut_16': xǁBitsǁ__getitem____mutmut_16
    }
    
    def __getitem__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__getitem____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__getitem____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getitem__.__signature__ = _mutmut_signature(xǁBitsǁ__getitem____mutmut_orig)
    xǁBitsǁ__getitem____mutmut_orig.__name__ = 'xǁBitsǁ__getitem__'

    def __len__(self):
        return self.len

    def xǁBitsǁ__eq____mutmut_orig(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.val == other.val and self.len == other.len

    def xǁBitsǁ__eq____mutmut_1(self, other):
        if type(None) is not type(other):
            return NotImplemented
        return self.val == other.val and self.len == other.len

    def xǁBitsǁ__eq____mutmut_2(self, other):
        if type(self) is type(other):
            return NotImplemented
        return self.val == other.val and self.len == other.len

    def xǁBitsǁ__eq____mutmut_3(self, other):
        if type(self) is not type(None):
            return NotImplemented
        return self.val == other.val and self.len == other.len

    def xǁBitsǁ__eq____mutmut_4(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.val == other.val or self.len == other.len

    def xǁBitsǁ__eq____mutmut_5(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.val != other.val and self.len == other.len

    def xǁBitsǁ__eq____mutmut_6(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.val == other.val and self.len != other.len
    
    xǁBitsǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__eq____mutmut_1': xǁBitsǁ__eq____mutmut_1, 
        'xǁBitsǁ__eq____mutmut_2': xǁBitsǁ__eq____mutmut_2, 
        'xǁBitsǁ__eq____mutmut_3': xǁBitsǁ__eq____mutmut_3, 
        'xǁBitsǁ__eq____mutmut_4': xǁBitsǁ__eq____mutmut_4, 
        'xǁBitsǁ__eq____mutmut_5': xǁBitsǁ__eq____mutmut_5, 
        'xǁBitsǁ__eq____mutmut_6': xǁBitsǁ__eq____mutmut_6
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁBitsǁ__eq____mutmut_orig)
    xǁBitsǁ__eq____mutmut_orig.__name__ = 'xǁBitsǁ__eq__'

    def xǁBitsǁ__or____mutmut_orig(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_1(self, other):
        if type(None) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_2(self, other):
        if type(self) is type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_3(self, other):
        if type(self) is not type(None):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_4(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(None, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_5(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, None)

    def xǁBitsǁ__or____mutmut_6(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_7(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, )

    def xǁBitsǁ__or____mutmut_8(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def xǁBitsǁ__or____mutmut_9(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(None, other.len))

    def xǁBitsǁ__or____mutmut_10(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, None))

    def xǁBitsǁ__or____mutmut_11(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(other.len))

    def xǁBitsǁ__or____mutmut_12(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, ))
    
    xǁBitsǁ__or____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__or____mutmut_1': xǁBitsǁ__or____mutmut_1, 
        'xǁBitsǁ__or____mutmut_2': xǁBitsǁ__or____mutmut_2, 
        'xǁBitsǁ__or____mutmut_3': xǁBitsǁ__or____mutmut_3, 
        'xǁBitsǁ__or____mutmut_4': xǁBitsǁ__or____mutmut_4, 
        'xǁBitsǁ__or____mutmut_5': xǁBitsǁ__or____mutmut_5, 
        'xǁBitsǁ__or____mutmut_6': xǁBitsǁ__or____mutmut_6, 
        'xǁBitsǁ__or____mutmut_7': xǁBitsǁ__or____mutmut_7, 
        'xǁBitsǁ__or____mutmut_8': xǁBitsǁ__or____mutmut_8, 
        'xǁBitsǁ__or____mutmut_9': xǁBitsǁ__or____mutmut_9, 
        'xǁBitsǁ__or____mutmut_10': xǁBitsǁ__or____mutmut_10, 
        'xǁBitsǁ__or____mutmut_11': xǁBitsǁ__or____mutmut_11, 
        'xǁBitsǁ__or____mutmut_12': xǁBitsǁ__or____mutmut_12
    }
    
    def __or__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__or____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__or____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __or__.__signature__ = _mutmut_signature(xǁBitsǁ__or____mutmut_orig)
    xǁBitsǁ__or____mutmut_orig.__name__ = 'xǁBitsǁ__or__'

    def xǁBitsǁ__and____mutmut_orig(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_1(self, other):
        if type(None) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_2(self, other):
        if type(self) is type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_3(self, other):
        if type(self) is not type(None):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_4(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(None, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_5(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, None)

    def xǁBitsǁ__and____mutmut_6(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_7(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, )

    def xǁBitsǁ__and____mutmut_8(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val | other.val, max(self.len, other.len))

    def xǁBitsǁ__and____mutmut_9(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(None, other.len))

    def xǁBitsǁ__and____mutmut_10(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, None))

    def xǁBitsǁ__and____mutmut_11(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(other.len))

    def xǁBitsǁ__and____mutmut_12(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return Bits(self.val & other.val, max(self.len, ))
    
    xǁBitsǁ__and____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__and____mutmut_1': xǁBitsǁ__and____mutmut_1, 
        'xǁBitsǁ__and____mutmut_2': xǁBitsǁ__and____mutmut_2, 
        'xǁBitsǁ__and____mutmut_3': xǁBitsǁ__and____mutmut_3, 
        'xǁBitsǁ__and____mutmut_4': xǁBitsǁ__and____mutmut_4, 
        'xǁBitsǁ__and____mutmut_5': xǁBitsǁ__and____mutmut_5, 
        'xǁBitsǁ__and____mutmut_6': xǁBitsǁ__and____mutmut_6, 
        'xǁBitsǁ__and____mutmut_7': xǁBitsǁ__and____mutmut_7, 
        'xǁBitsǁ__and____mutmut_8': xǁBitsǁ__and____mutmut_8, 
        'xǁBitsǁ__and____mutmut_9': xǁBitsǁ__and____mutmut_9, 
        'xǁBitsǁ__and____mutmut_10': xǁBitsǁ__and____mutmut_10, 
        'xǁBitsǁ__and____mutmut_11': xǁBitsǁ__and____mutmut_11, 
        'xǁBitsǁ__and____mutmut_12': xǁBitsǁ__and____mutmut_12
    }
    
    def __and__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__and____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__and____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __and__.__signature__ = _mutmut_signature(xǁBitsǁ__and____mutmut_orig)
    xǁBitsǁ__and____mutmut_orig.__name__ = 'xǁBitsǁ__and__'

    def xǁBitsǁ__lshift____mutmut_orig(self, other):
        return Bits(self.val << other, self.len + other)

    def xǁBitsǁ__lshift____mutmut_1(self, other):
        return Bits(None, self.len + other)

    def xǁBitsǁ__lshift____mutmut_2(self, other):
        return Bits(self.val << other, None)

    def xǁBitsǁ__lshift____mutmut_3(self, other):
        return Bits(self.len + other)

    def xǁBitsǁ__lshift____mutmut_4(self, other):
        return Bits(self.val << other, )

    def xǁBitsǁ__lshift____mutmut_5(self, other):
        return Bits(self.val >> other, self.len + other)

    def xǁBitsǁ__lshift____mutmut_6(self, other):
        return Bits(self.val << other, self.len - other)
    
    xǁBitsǁ__lshift____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__lshift____mutmut_1': xǁBitsǁ__lshift____mutmut_1, 
        'xǁBitsǁ__lshift____mutmut_2': xǁBitsǁ__lshift____mutmut_2, 
        'xǁBitsǁ__lshift____mutmut_3': xǁBitsǁ__lshift____mutmut_3, 
        'xǁBitsǁ__lshift____mutmut_4': xǁBitsǁ__lshift____mutmut_4, 
        'xǁBitsǁ__lshift____mutmut_5': xǁBitsǁ__lshift____mutmut_5, 
        'xǁBitsǁ__lshift____mutmut_6': xǁBitsǁ__lshift____mutmut_6
    }
    
    def __lshift__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__lshift____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__lshift____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __lshift__.__signature__ = _mutmut_signature(xǁBitsǁ__lshift____mutmut_orig)
    xǁBitsǁ__lshift____mutmut_orig.__name__ = 'xǁBitsǁ__lshift__'

    def xǁBitsǁ__rshift____mutmut_orig(self, other):
        return Bits(self.val >> other, self.len - other)

    def xǁBitsǁ__rshift____mutmut_1(self, other):
        return Bits(None, self.len - other)

    def xǁBitsǁ__rshift____mutmut_2(self, other):
        return Bits(self.val >> other, None)

    def xǁBitsǁ__rshift____mutmut_3(self, other):
        return Bits(self.len - other)

    def xǁBitsǁ__rshift____mutmut_4(self, other):
        return Bits(self.val >> other, )

    def xǁBitsǁ__rshift____mutmut_5(self, other):
        return Bits(self.val << other, self.len - other)

    def xǁBitsǁ__rshift____mutmut_6(self, other):
        return Bits(self.val >> other, self.len + other)
    
    xǁBitsǁ__rshift____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__rshift____mutmut_1': xǁBitsǁ__rshift____mutmut_1, 
        'xǁBitsǁ__rshift____mutmut_2': xǁBitsǁ__rshift____mutmut_2, 
        'xǁBitsǁ__rshift____mutmut_3': xǁBitsǁ__rshift____mutmut_3, 
        'xǁBitsǁ__rshift____mutmut_4': xǁBitsǁ__rshift____mutmut_4, 
        'xǁBitsǁ__rshift____mutmut_5': xǁBitsǁ__rshift____mutmut_5, 
        'xǁBitsǁ__rshift____mutmut_6': xǁBitsǁ__rshift____mutmut_6
    }
    
    def __rshift__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__rshift____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__rshift____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __rshift__.__signature__ = _mutmut_signature(xǁBitsǁ__rshift____mutmut_orig)
    xǁBitsǁ__rshift____mutmut_orig.__name__ = 'xǁBitsǁ__rshift__'

    def xǁBitsǁ__hash____mutmut_orig(self):
        return hash(self.val)

    def xǁBitsǁ__hash____mutmut_1(self):
        return hash(None)
    
    xǁBitsǁ__hash____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__hash____mutmut_1': xǁBitsǁ__hash____mutmut_1
    }
    
    def __hash__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__hash____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__hash____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __hash__.__signature__ = _mutmut_signature(xǁBitsǁ__hash____mutmut_orig)
    xǁBitsǁ__hash____mutmut_orig.__name__ = 'xǁBitsǁ__hash__'

    def xǁBitsǁas_list__mutmut_orig(self):
        return [c == '1' for c in self.as_bin()]

    def xǁBitsǁas_list__mutmut_1(self):
        return [c != '1' for c in self.as_bin()]

    def xǁBitsǁas_list__mutmut_2(self):
        return [c == 'XX1XX' for c in self.as_bin()]
    
    xǁBitsǁas_list__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁas_list__mutmut_1': xǁBitsǁas_list__mutmut_1, 
        'xǁBitsǁas_list__mutmut_2': xǁBitsǁas_list__mutmut_2
    }
    
    def as_list(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁas_list__mutmut_orig"), object.__getattribute__(self, "xǁBitsǁas_list__mutmut_mutants"), args, kwargs, self)
        return result 
    
    as_list.__signature__ = _mutmut_signature(xǁBitsǁas_list__mutmut_orig)
    xǁBitsǁas_list__mutmut_orig.__name__ = 'xǁBitsǁas_list'

    def xǁBitsǁas_bin__mutmut_orig(self):
        return f'{{0:0{self.len}b}}'.format(self.val)

    def xǁBitsǁas_bin__mutmut_1(self):
        return f'{{0:0{self.len}b}}'.format(None)
    
    xǁBitsǁas_bin__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁas_bin__mutmut_1': xǁBitsǁas_bin__mutmut_1
    }
    
    def as_bin(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁas_bin__mutmut_orig"), object.__getattribute__(self, "xǁBitsǁas_bin__mutmut_mutants"), args, kwargs, self)
        return result 
    
    as_bin.__signature__ = _mutmut_signature(xǁBitsǁas_bin__mutmut_orig)
    xǁBitsǁas_bin__mutmut_orig.__name__ = 'xǁBitsǁas_bin'

    def xǁBitsǁas_hex__mutmut_orig(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_1(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = None
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_2(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 / (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_3(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{3 * (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_4(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 - ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_5(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len / 8 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_6(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 9 + ((self.len % 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_7(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len / 8) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_8(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 9) != 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_9(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) == 0))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_10(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) != 1))}X'
        ret = tmpl % self.val
        return ret

    def xǁBitsǁas_hex__mutmut_11(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = None
        return ret

    def xǁBitsǁas_hex__mutmut_12(self):
        # make template to pad out to number of bytes necessary to represent bits
        tmpl = f'%0{2 * (self.len // 8 + ((self.len % 8) != 0))}X'
        ret = tmpl / self.val
        return ret
    
    xǁBitsǁas_hex__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁas_hex__mutmut_1': xǁBitsǁas_hex__mutmut_1, 
        'xǁBitsǁas_hex__mutmut_2': xǁBitsǁas_hex__mutmut_2, 
        'xǁBitsǁas_hex__mutmut_3': xǁBitsǁas_hex__mutmut_3, 
        'xǁBitsǁas_hex__mutmut_4': xǁBitsǁas_hex__mutmut_4, 
        'xǁBitsǁas_hex__mutmut_5': xǁBitsǁas_hex__mutmut_5, 
        'xǁBitsǁas_hex__mutmut_6': xǁBitsǁas_hex__mutmut_6, 
        'xǁBitsǁas_hex__mutmut_7': xǁBitsǁas_hex__mutmut_7, 
        'xǁBitsǁas_hex__mutmut_8': xǁBitsǁas_hex__mutmut_8, 
        'xǁBitsǁas_hex__mutmut_9': xǁBitsǁas_hex__mutmut_9, 
        'xǁBitsǁas_hex__mutmut_10': xǁBitsǁas_hex__mutmut_10, 
        'xǁBitsǁas_hex__mutmut_11': xǁBitsǁas_hex__mutmut_11, 
        'xǁBitsǁas_hex__mutmut_12': xǁBitsǁas_hex__mutmut_12
    }
    
    def as_hex(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁas_hex__mutmut_orig"), object.__getattribute__(self, "xǁBitsǁas_hex__mutmut_mutants"), args, kwargs, self)
        return result 
    
    as_hex.__signature__ = _mutmut_signature(xǁBitsǁas_hex__mutmut_orig)
    xǁBitsǁas_hex__mutmut_orig.__name__ = 'xǁBitsǁas_hex'

    def as_int(self):
        return self.val

    def xǁBitsǁas_bytes__mutmut_orig(self):
        return binascii.unhexlify(self.as_hex())

    def xǁBitsǁas_bytes__mutmut_1(self):
        return binascii.unhexlify(None)
    
    xǁBitsǁas_bytes__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁas_bytes__mutmut_1': xǁBitsǁas_bytes__mutmut_1
    }
    
    def as_bytes(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁas_bytes__mutmut_orig"), object.__getattribute__(self, "xǁBitsǁas_bytes__mutmut_mutants"), args, kwargs, self)
        return result 
    
    as_bytes.__signature__ = _mutmut_signature(xǁBitsǁas_bytes__mutmut_orig)
    xǁBitsǁas_bytes__mutmut_orig.__name__ = 'xǁBitsǁas_bytes'

    @classmethod
    def from_list(cls, list_):
        return cls(list_)

    @classmethod
    def from_bin(cls, bin):
        return cls(bin)

    @classmethod
    def from_hex(cls, hex):
        if isinstance(hex, bytes):
            hex = hex.decode('ascii')
        if not hex.startswith('0x'):
            hex = '0x' + hex
        return cls(hex)

    @classmethod
    def from_int(cls, int_, len_=None):
        return cls(int_, len_)

    @classmethod
    def from_bytes(cls, bytes_):
        return cls.from_hex(binascii.hexlify(bytes_))

    def xǁBitsǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return f"{cn}('{self.as_bin()}')"

    def xǁBitsǁ__repr____mutmut_1(self):
        cn = None
        return f"{cn}('{self.as_bin()}')"
    
    xǁBitsǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBitsǁ__repr____mutmut_1': xǁBitsǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBitsǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁBitsǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁBitsǁ__repr____mutmut_orig)
    xǁBitsǁ__repr____mutmut_orig.__name__ = 'xǁBitsǁ__repr__'
