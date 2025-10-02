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

"""``statsutils`` provides tools aimed primarily at descriptive
statistics for data analysis, such as :func:`mean` (average),
:func:`median`, :func:`variance`, and many others,

The :class:`Stats` type provides all the main functionality of the
``statsutils`` module. A :class:`Stats` object wraps a given dataset,
providing all statistical measures as property attributes. These
attributes cache their results, which allows efficient computation of
multiple measures, as many measures rely on other measures. For
example, relative standard deviation (:attr:`Stats.rel_std_dev`)
relies on both the mean and standard deviation. The Stats object
caches those results so no rework is done.

The :class:`Stats` type's attributes have module-level counterparts for
convenience when the computation reuse advantages do not apply.

>>> stats = Stats(range(42))
>>> stats.mean
20.5
>>> mean(range(42))
20.5

Statistics is a large field, and ``statsutils`` is focused on a few
basic techniques that are useful in software. The following is a brief
introduction to those techniques. For a more in-depth introduction,
`Statistics for Software
<https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_,
an article I wrote on the topic. It introduces key terminology vital
to effective usage of statistics.

Statistical moments
-------------------

Python programmers are probably familiar with the concept of the
*mean* or *average*, which gives a rough quantitiative middle value by
which a sample can be can be generalized. However, the mean is just
the first of four `moment`_-based measures by which a sample or
distribution can be measured.

The four `Standardized moments`_ are:

  1. `Mean`_ - :func:`mean` - theoretical middle value
  2. `Variance`_ - :func:`variance` - width of value dispersion
  3. `Skewness`_ - :func:`skewness` - symmetry of distribution
  4. `Kurtosis`_ - :func:`kurtosis` - "peakiness" or "long-tailed"-ness

For more information check out `the Moment article on Wikipedia`_.

.. _moment: https://en.wikipedia.org/wiki/Moment_(mathematics)
.. _Standardized moments: https://en.wikipedia.org/wiki/Standardized_moment
.. _Mean: https://en.wikipedia.org/wiki/Mean
.. _Variance: https://en.wikipedia.org/wiki/Variance
.. _Skewness: https://en.wikipedia.org/wiki/Skewness
.. _Kurtosis: https://en.wikipedia.org/wiki/Kurtosis
.. _the Moment article on Wikipedia: https://en.wikipedia.org/wiki/Moment_(mathematics)

Keep in mind that while these moments can give a bit more insight into
the shape and distribution of data, they do not guarantee a complete
picture. Wildly different datasets can have the same values for all
four moments, so generalize wisely.

Robust statistics
-----------------

Moment-based statistics are notorious for being easily skewed by
outliers. The whole field of robust statistics aims to mitigate this
dilemma. ``statsutils`` also includes several robust statistical methods:

  * `Median`_ - The middle value of a sorted dataset
  * `Trimean`_ - Another robust measure of the data's central tendency
  * `Median Absolute Deviation`_ (MAD) - A robust measure of
    variability, a natural counterpart to :func:`variance`.
  * `Trimming`_ - Reducing a dataset to only the middle majority of
    data is a simple way of making other estimators more robust.

.. _Median: https://en.wikipedia.org/wiki/Median
.. _Trimean: https://en.wikipedia.org/wiki/Trimean
.. _Median Absolute Deviation: https://en.wikipedia.org/wiki/Median_absolute_deviation
.. _Trimming: https://en.wikipedia.org/wiki/Trimmed_estimator


Online and Offline Statistics
-----------------------------

Unrelated to computer networking, `online`_ statistics involve
calculating statistics in a `streaming`_ fashion, without all the data
being available. The :class:`Stats` type is meant for the more
traditional offline statistics when all the data is available. For
pure-Python online statistics accumulators, look at the `Lithoxyl`_
system instrumentation package.

.. _Online: https://en.wikipedia.org/wiki/Online_algorithm
.. _streaming: https://en.wikipedia.org/wiki/Streaming_algorithm
.. _Lithoxyl: https://github.com/mahmoud/lithoxyl

"""


import bisect
from math import floor, ceil
from collections import Counter
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


class _StatsProperty:
    def xǁ_StatsPropertyǁ__init____mutmut_orig(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_1(self, name, func):
        self.name = None
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_2(self, name, func):
        self.name = name
        self.func = None
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_3(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = None

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_4(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' - name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_5(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = 'XX_XX' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_6(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = None
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_7(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ and ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_8(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or 'XXXX'
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_9(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = None
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_10(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition(None)
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_11(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.rpartition('>>>')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_12(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('XX>>>XX')
        self.__doc__ = pre_doctest_doc
    def xǁ_StatsPropertyǁ__init____mutmut_13(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = None
    
    xǁ_StatsPropertyǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_StatsPropertyǁ__init____mutmut_1': xǁ_StatsPropertyǁ__init____mutmut_1, 
        'xǁ_StatsPropertyǁ__init____mutmut_2': xǁ_StatsPropertyǁ__init____mutmut_2, 
        'xǁ_StatsPropertyǁ__init____mutmut_3': xǁ_StatsPropertyǁ__init____mutmut_3, 
        'xǁ_StatsPropertyǁ__init____mutmut_4': xǁ_StatsPropertyǁ__init____mutmut_4, 
        'xǁ_StatsPropertyǁ__init____mutmut_5': xǁ_StatsPropertyǁ__init____mutmut_5, 
        'xǁ_StatsPropertyǁ__init____mutmut_6': xǁ_StatsPropertyǁ__init____mutmut_6, 
        'xǁ_StatsPropertyǁ__init____mutmut_7': xǁ_StatsPropertyǁ__init____mutmut_7, 
        'xǁ_StatsPropertyǁ__init____mutmut_8': xǁ_StatsPropertyǁ__init____mutmut_8, 
        'xǁ_StatsPropertyǁ__init____mutmut_9': xǁ_StatsPropertyǁ__init____mutmut_9, 
        'xǁ_StatsPropertyǁ__init____mutmut_10': xǁ_StatsPropertyǁ__init____mutmut_10, 
        'xǁ_StatsPropertyǁ__init____mutmut_11': xǁ_StatsPropertyǁ__init____mutmut_11, 
        'xǁ_StatsPropertyǁ__init____mutmut_12': xǁ_StatsPropertyǁ__init____mutmut_12, 
        'xǁ_StatsPropertyǁ__init____mutmut_13': xǁ_StatsPropertyǁ__init____mutmut_13
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_StatsPropertyǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁ_StatsPropertyǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁ_StatsPropertyǁ__init____mutmut_orig)
    xǁ_StatsPropertyǁ__init____mutmut_orig.__name__ = 'xǁ_StatsPropertyǁ__init__'

    def xǁ_StatsPropertyǁ__get____mutmut_orig(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_1(self, obj, objtype=None):
        if obj is not None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_2(self, obj, objtype=None):
        if obj is None:
            return self
        if obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_3(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(None, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_4(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, None)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_5(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_6(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, )
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_7(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(None, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_8(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, None, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_9(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, None)
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_10(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_11(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.func(obj))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_12(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, )
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_13(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(None))
            return getattr(obj, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_14(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(None, self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_15(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, None)

    def xǁ_StatsPropertyǁ__get____mutmut_16(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(self.internal_name)

    def xǁ_StatsPropertyǁ__get____mutmut_17(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, )
    
    xǁ_StatsPropertyǁ__get____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁ_StatsPropertyǁ__get____mutmut_1': xǁ_StatsPropertyǁ__get____mutmut_1, 
        'xǁ_StatsPropertyǁ__get____mutmut_2': xǁ_StatsPropertyǁ__get____mutmut_2, 
        'xǁ_StatsPropertyǁ__get____mutmut_3': xǁ_StatsPropertyǁ__get____mutmut_3, 
        'xǁ_StatsPropertyǁ__get____mutmut_4': xǁ_StatsPropertyǁ__get____mutmut_4, 
        'xǁ_StatsPropertyǁ__get____mutmut_5': xǁ_StatsPropertyǁ__get____mutmut_5, 
        'xǁ_StatsPropertyǁ__get____mutmut_6': xǁ_StatsPropertyǁ__get____mutmut_6, 
        'xǁ_StatsPropertyǁ__get____mutmut_7': xǁ_StatsPropertyǁ__get____mutmut_7, 
        'xǁ_StatsPropertyǁ__get____mutmut_8': xǁ_StatsPropertyǁ__get____mutmut_8, 
        'xǁ_StatsPropertyǁ__get____mutmut_9': xǁ_StatsPropertyǁ__get____mutmut_9, 
        'xǁ_StatsPropertyǁ__get____mutmut_10': xǁ_StatsPropertyǁ__get____mutmut_10, 
        'xǁ_StatsPropertyǁ__get____mutmut_11': xǁ_StatsPropertyǁ__get____mutmut_11, 
        'xǁ_StatsPropertyǁ__get____mutmut_12': xǁ_StatsPropertyǁ__get____mutmut_12, 
        'xǁ_StatsPropertyǁ__get____mutmut_13': xǁ_StatsPropertyǁ__get____mutmut_13, 
        'xǁ_StatsPropertyǁ__get____mutmut_14': xǁ_StatsPropertyǁ__get____mutmut_14, 
        'xǁ_StatsPropertyǁ__get____mutmut_15': xǁ_StatsPropertyǁ__get____mutmut_15, 
        'xǁ_StatsPropertyǁ__get____mutmut_16': xǁ_StatsPropertyǁ__get____mutmut_16, 
        'xǁ_StatsPropertyǁ__get____mutmut_17': xǁ_StatsPropertyǁ__get____mutmut_17
    }
    
    def __get__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁ_StatsPropertyǁ__get____mutmut_orig"), object.__getattribute__(self, "xǁ_StatsPropertyǁ__get____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __get__.__signature__ = _mutmut_signature(xǁ_StatsPropertyǁ__get____mutmut_orig)
    xǁ_StatsPropertyǁ__get____mutmut_orig.__name__ = 'xǁ_StatsPropertyǁ__get__'


class Stats:
    """The ``Stats`` type is used to represent a group of unordered
    statistical datapoints for calculations such as mean, median, and
    variance.

    Args:

        data (list): List or other iterable containing numeric values.
        default (float): A value to be returned when a given
            statistical measure is not defined. 0.0 by default, but
            ``float('nan')`` is appropriate for stricter applications.
        use_copy (bool): By default Stats objects copy the initial
            data into a new list to avoid issues with
            modifications. Pass ``False`` to disable this behavior.
        is_sorted (bool): Presorted data can skip an extra sorting
            step for a little speed boost. Defaults to False.

    """
    def xǁStatsǁ__init____mutmut_orig(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_1(self, data, default=1.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_2(self, data, default=0.0, use_copy=False, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_3(self, data, default=0.0, use_copy=True, is_sorted=True):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_4(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = None
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_5(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = None
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_6(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = None
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_7(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(None)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_8(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = None

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_9(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = None
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_10(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = None
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_11(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = None
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_12(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(None)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0
    def xǁStatsǁ__init____mutmut_13(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = None
    def xǁStatsǁ__init____mutmut_14(self, data, default=0.0, use_copy=True, is_sorted=False):
        self._use_copy = use_copy
        self._is_sorted = is_sorted
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 1
    
    xǁStatsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ__init____mutmut_1': xǁStatsǁ__init____mutmut_1, 
        'xǁStatsǁ__init____mutmut_2': xǁStatsǁ__init____mutmut_2, 
        'xǁStatsǁ__init____mutmut_3': xǁStatsǁ__init____mutmut_3, 
        'xǁStatsǁ__init____mutmut_4': xǁStatsǁ__init____mutmut_4, 
        'xǁStatsǁ__init____mutmut_5': xǁStatsǁ__init____mutmut_5, 
        'xǁStatsǁ__init____mutmut_6': xǁStatsǁ__init____mutmut_6, 
        'xǁStatsǁ__init____mutmut_7': xǁStatsǁ__init____mutmut_7, 
        'xǁStatsǁ__init____mutmut_8': xǁStatsǁ__init____mutmut_8, 
        'xǁStatsǁ__init____mutmut_9': xǁStatsǁ__init____mutmut_9, 
        'xǁStatsǁ__init____mutmut_10': xǁStatsǁ__init____mutmut_10, 
        'xǁStatsǁ__init____mutmut_11': xǁStatsǁ__init____mutmut_11, 
        'xǁStatsǁ__init____mutmut_12': xǁStatsǁ__init____mutmut_12, 
        'xǁStatsǁ__init____mutmut_13': xǁStatsǁ__init____mutmut_13, 
        'xǁStatsǁ__init____mutmut_14': xǁStatsǁ__init____mutmut_14
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁStatsǁ__init____mutmut_orig)
    xǁStatsǁ__init____mutmut_orig.__name__ = 'xǁStatsǁ__init__'

    def __len__(self):
        return len(self.data)

    def xǁStatsǁ__iter____mutmut_orig(self):
        return iter(self.data)

    def xǁStatsǁ__iter____mutmut_1(self):
        return iter(None)
    
    xǁStatsǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ__iter____mutmut_1': xǁStatsǁ__iter____mutmut_1
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁStatsǁ__iter____mutmut_orig)
    xǁStatsǁ__iter____mutmut_orig.__name__ = 'xǁStatsǁ__iter__'

    def xǁStatsǁ_get_sorted_data__mutmut_orig(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if not self._use_copy:
            return sorted(self.data)
        elif not self._is_sorted:
            self.data.sort()
        return self.data

    def xǁStatsǁ_get_sorted_data__mutmut_1(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if self._use_copy:
            return sorted(self.data)
        elif not self._is_sorted:
            self.data.sort()
        return self.data

    def xǁStatsǁ_get_sorted_data__mutmut_2(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if not self._use_copy:
            return sorted(None)
        elif not self._is_sorted:
            self.data.sort()
        return self.data

    def xǁStatsǁ_get_sorted_data__mutmut_3(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if not self._use_copy:
            return sorted(self.data)
        elif self._is_sorted:
            self.data.sort()
        return self.data
    
    xǁStatsǁ_get_sorted_data__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_get_sorted_data__mutmut_1': xǁStatsǁ_get_sorted_data__mutmut_1, 
        'xǁStatsǁ_get_sorted_data__mutmut_2': xǁStatsǁ_get_sorted_data__mutmut_2, 
        'xǁStatsǁ_get_sorted_data__mutmut_3': xǁStatsǁ_get_sorted_data__mutmut_3
    }
    
    def _get_sorted_data(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_get_sorted_data__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_get_sorted_data__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_sorted_data.__signature__ = _mutmut_signature(xǁStatsǁ_get_sorted_data__mutmut_orig)
    xǁStatsǁ_get_sorted_data__mutmut_orig.__name__ = 'xǁStatsǁ_get_sorted_data'

    def xǁStatsǁclear_cache__mutmut_orig(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_1(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = None
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_2(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(None, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_3(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, None).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_4(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_5(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, ).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_6(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if hasattr(self, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_7(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(None, attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_8(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, None):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_9(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(attr_name):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_10(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, ):
                continue
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_11(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                break
            delattr(self, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_12(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(None, attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_13(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, None)
        return

    def xǁStatsǁclear_cache__mutmut_14(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(attr_name)
        return

    def xǁStatsǁclear_cache__mutmut_15(self):
        """``Stats`` objects automatically cache intermediary calculations
        that can be reused. For instance, accessing the ``std_dev``
        attribute after the ``variance`` attribute will be
        significantly faster for medium-to-large datasets.

        If you modify the object by adding additional data points,
        call this function to have the cached statistics recomputed.

        """
        for attr_name in self._prop_attr_names:
            attr_name = getattr(self.__class__, attr_name).internal_name
            if not hasattr(self, attr_name):
                continue
            delattr(self, )
        return
    
    xǁStatsǁclear_cache__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁclear_cache__mutmut_1': xǁStatsǁclear_cache__mutmut_1, 
        'xǁStatsǁclear_cache__mutmut_2': xǁStatsǁclear_cache__mutmut_2, 
        'xǁStatsǁclear_cache__mutmut_3': xǁStatsǁclear_cache__mutmut_3, 
        'xǁStatsǁclear_cache__mutmut_4': xǁStatsǁclear_cache__mutmut_4, 
        'xǁStatsǁclear_cache__mutmut_5': xǁStatsǁclear_cache__mutmut_5, 
        'xǁStatsǁclear_cache__mutmut_6': xǁStatsǁclear_cache__mutmut_6, 
        'xǁStatsǁclear_cache__mutmut_7': xǁStatsǁclear_cache__mutmut_7, 
        'xǁStatsǁclear_cache__mutmut_8': xǁStatsǁclear_cache__mutmut_8, 
        'xǁStatsǁclear_cache__mutmut_9': xǁStatsǁclear_cache__mutmut_9, 
        'xǁStatsǁclear_cache__mutmut_10': xǁStatsǁclear_cache__mutmut_10, 
        'xǁStatsǁclear_cache__mutmut_11': xǁStatsǁclear_cache__mutmut_11, 
        'xǁStatsǁclear_cache__mutmut_12': xǁStatsǁclear_cache__mutmut_12, 
        'xǁStatsǁclear_cache__mutmut_13': xǁStatsǁclear_cache__mutmut_13, 
        'xǁStatsǁclear_cache__mutmut_14': xǁStatsǁclear_cache__mutmut_14, 
        'xǁStatsǁclear_cache__mutmut_15': xǁStatsǁclear_cache__mutmut_15
    }
    
    def clear_cache(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁclear_cache__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁclear_cache__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_cache.__signature__ = _mutmut_signature(xǁStatsǁclear_cache__mutmut_orig)
    xǁStatsǁclear_cache__mutmut_orig.__name__ = 'xǁStatsǁclear_cache'

    def _calc_count(self):
        """The number of items in this Stats object. Returns the same as
        :func:`len` on a Stats object, but provided for pandas terminology
        parallelism.

        >>> Stats(range(20)).count
        20
        """
        return len(self.data)
    count = _StatsProperty('count', _calc_count)

    def xǁStatsǁ_calc_mean__mutmut_orig(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, 0.0) / len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_1(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, 0.0) * len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_2(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(None, 0.0) / len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_3(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, None) / len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_4(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(0.0) / len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_5(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, ) / len(self.data)

    def xǁStatsǁ_calc_mean__mutmut_6(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, 1.0) / len(self.data)
    
    xǁStatsǁ_calc_mean__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_mean__mutmut_1': xǁStatsǁ_calc_mean__mutmut_1, 
        'xǁStatsǁ_calc_mean__mutmut_2': xǁStatsǁ_calc_mean__mutmut_2, 
        'xǁStatsǁ_calc_mean__mutmut_3': xǁStatsǁ_calc_mean__mutmut_3, 
        'xǁStatsǁ_calc_mean__mutmut_4': xǁStatsǁ_calc_mean__mutmut_4, 
        'xǁStatsǁ_calc_mean__mutmut_5': xǁStatsǁ_calc_mean__mutmut_5, 
        'xǁStatsǁ_calc_mean__mutmut_6': xǁStatsǁ_calc_mean__mutmut_6
    }
    
    def _calc_mean(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_mean__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_mean__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_mean.__signature__ = _mutmut_signature(xǁStatsǁ_calc_mean__mutmut_orig)
    xǁStatsǁ_calc_mean__mutmut_orig.__name__ = 'xǁStatsǁ_calc_mean'
    mean = _StatsProperty('mean', _calc_mean)

    def xǁStatsǁ_calc_max__mutmut_orig(self):
        """
        The maximum value present in the data.

        >>> Stats([2, 1, 3]).max
        3
        """
        if self._is_sorted:
            return self.data[-1]
        return max(self.data)

    def xǁStatsǁ_calc_max__mutmut_1(self):
        """
        The maximum value present in the data.

        >>> Stats([2, 1, 3]).max
        3
        """
        if self._is_sorted:
            return self.data[+1]
        return max(self.data)

    def xǁStatsǁ_calc_max__mutmut_2(self):
        """
        The maximum value present in the data.

        >>> Stats([2, 1, 3]).max
        3
        """
        if self._is_sorted:
            return self.data[-2]
        return max(self.data)

    def xǁStatsǁ_calc_max__mutmut_3(self):
        """
        The maximum value present in the data.

        >>> Stats([2, 1, 3]).max
        3
        """
        if self._is_sorted:
            return self.data[-1]
        return max(None)
    
    xǁStatsǁ_calc_max__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_max__mutmut_1': xǁStatsǁ_calc_max__mutmut_1, 
        'xǁStatsǁ_calc_max__mutmut_2': xǁStatsǁ_calc_max__mutmut_2, 
        'xǁStatsǁ_calc_max__mutmut_3': xǁStatsǁ_calc_max__mutmut_3
    }
    
    def _calc_max(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_max__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_max__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_max.__signature__ = _mutmut_signature(xǁStatsǁ_calc_max__mutmut_orig)
    xǁStatsǁ_calc_max__mutmut_orig.__name__ = 'xǁStatsǁ_calc_max'
    max = _StatsProperty('max', _calc_max)

    def xǁStatsǁ_calc_min__mutmut_orig(self):
        """
        The minimum value present in the data.

        >>> Stats([2, 1, 3]).min
        1
        """
        if self._is_sorted:
            return self.data[0]
        return min(self.data)

    def xǁStatsǁ_calc_min__mutmut_1(self):
        """
        The minimum value present in the data.

        >>> Stats([2, 1, 3]).min
        1
        """
        if self._is_sorted:
            return self.data[1]
        return min(self.data)

    def xǁStatsǁ_calc_min__mutmut_2(self):
        """
        The minimum value present in the data.

        >>> Stats([2, 1, 3]).min
        1
        """
        if self._is_sorted:
            return self.data[0]
        return min(None)
    
    xǁStatsǁ_calc_min__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_min__mutmut_1': xǁStatsǁ_calc_min__mutmut_1, 
        'xǁStatsǁ_calc_min__mutmut_2': xǁStatsǁ_calc_min__mutmut_2
    }
    
    def _calc_min(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_min__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_min__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_min.__signature__ = _mutmut_signature(xǁStatsǁ_calc_min__mutmut_orig)
    xǁStatsǁ_calc_min__mutmut_orig.__name__ = 'xǁStatsǁ_calc_min'
    min = _StatsProperty('min', _calc_min)

    def xǁStatsǁ_calc_median__mutmut_orig(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), 0.5)

    def xǁStatsǁ_calc_median__mutmut_1(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(None, 0.5)

    def xǁStatsǁ_calc_median__mutmut_2(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), None)

    def xǁStatsǁ_calc_median__mutmut_3(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(0.5)

    def xǁStatsǁ_calc_median__mutmut_4(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), )

    def xǁStatsǁ_calc_median__mutmut_5(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), 1.5)
    
    xǁStatsǁ_calc_median__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_median__mutmut_1': xǁStatsǁ_calc_median__mutmut_1, 
        'xǁStatsǁ_calc_median__mutmut_2': xǁStatsǁ_calc_median__mutmut_2, 
        'xǁStatsǁ_calc_median__mutmut_3': xǁStatsǁ_calc_median__mutmut_3, 
        'xǁStatsǁ_calc_median__mutmut_4': xǁStatsǁ_calc_median__mutmut_4, 
        'xǁStatsǁ_calc_median__mutmut_5': xǁStatsǁ_calc_median__mutmut_5
    }
    
    def _calc_median(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_median__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_median__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_median.__signature__ = _mutmut_signature(xǁStatsǁ_calc_median__mutmut_orig)
    xǁStatsǁ_calc_median__mutmut_orig.__name__ = 'xǁStatsǁ_calc_median'
    median = _StatsProperty('median', _calc_median)

    def xǁStatsǁ_calc_iqr__mutmut_orig(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(0.75) - self.get_quantile(0.25)

    def xǁStatsǁ_calc_iqr__mutmut_1(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(0.75) + self.get_quantile(0.25)

    def xǁStatsǁ_calc_iqr__mutmut_2(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(None) - self.get_quantile(0.25)

    def xǁStatsǁ_calc_iqr__mutmut_3(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(1.75) - self.get_quantile(0.25)

    def xǁStatsǁ_calc_iqr__mutmut_4(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(0.75) - self.get_quantile(None)

    def xǁStatsǁ_calc_iqr__mutmut_5(self):
        """Inter-quartile range (IQR) is the difference between the 75th
        percentile and 25th percentile. IQR is a robust measure of
        dispersion, like standard deviation, but safer to compare
        between datasets, as it is less influenced by outliers.

        >>> iqr([1, 2, 3, 4, 5])
        2
        >>> iqr(range(1001))
        500
        """
        return self.get_quantile(0.75) - self.get_quantile(1.25)
    
    xǁStatsǁ_calc_iqr__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_iqr__mutmut_1': xǁStatsǁ_calc_iqr__mutmut_1, 
        'xǁStatsǁ_calc_iqr__mutmut_2': xǁStatsǁ_calc_iqr__mutmut_2, 
        'xǁStatsǁ_calc_iqr__mutmut_3': xǁStatsǁ_calc_iqr__mutmut_3, 
        'xǁStatsǁ_calc_iqr__mutmut_4': xǁStatsǁ_calc_iqr__mutmut_4, 
        'xǁStatsǁ_calc_iqr__mutmut_5': xǁStatsǁ_calc_iqr__mutmut_5
    }
    
    def _calc_iqr(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_iqr__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_iqr__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_iqr.__signature__ = _mutmut_signature(xǁStatsǁ_calc_iqr__mutmut_orig)
    xǁStatsǁ_calc_iqr__mutmut_orig.__name__ = 'xǁStatsǁ_calc_iqr'
    iqr = _StatsProperty('iqr', _calc_iqr)

    def xǁStatsǁ_calc_trimean__mutmut_orig(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_1(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = None
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_2(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = None
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_3(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: None
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_4(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(None, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_5(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, None)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_6(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_7(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, )
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_8(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) * 4.0

    def xǁStatsǁ_calc_trimean__mutmut_9(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) - gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_10(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) - (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_11(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(None) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_12(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(1.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_13(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 / gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_14(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (3 * gq(0.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_15(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(None)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_16(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(1.5)) + gq(0.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_17(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(None)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_18(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(1.75)) / 4.0

    def xǁStatsǁ_calc_trimean__mutmut_19(self):
        """The trimean is a robust measure of central tendency, like the
        median, that takes the weighted average of the median and the
        upper and lower quartiles.

        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0

        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 5.0
    
    xǁStatsǁ_calc_trimean__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_trimean__mutmut_1': xǁStatsǁ_calc_trimean__mutmut_1, 
        'xǁStatsǁ_calc_trimean__mutmut_2': xǁStatsǁ_calc_trimean__mutmut_2, 
        'xǁStatsǁ_calc_trimean__mutmut_3': xǁStatsǁ_calc_trimean__mutmut_3, 
        'xǁStatsǁ_calc_trimean__mutmut_4': xǁStatsǁ_calc_trimean__mutmut_4, 
        'xǁStatsǁ_calc_trimean__mutmut_5': xǁStatsǁ_calc_trimean__mutmut_5, 
        'xǁStatsǁ_calc_trimean__mutmut_6': xǁStatsǁ_calc_trimean__mutmut_6, 
        'xǁStatsǁ_calc_trimean__mutmut_7': xǁStatsǁ_calc_trimean__mutmut_7, 
        'xǁStatsǁ_calc_trimean__mutmut_8': xǁStatsǁ_calc_trimean__mutmut_8, 
        'xǁStatsǁ_calc_trimean__mutmut_9': xǁStatsǁ_calc_trimean__mutmut_9, 
        'xǁStatsǁ_calc_trimean__mutmut_10': xǁStatsǁ_calc_trimean__mutmut_10, 
        'xǁStatsǁ_calc_trimean__mutmut_11': xǁStatsǁ_calc_trimean__mutmut_11, 
        'xǁStatsǁ_calc_trimean__mutmut_12': xǁStatsǁ_calc_trimean__mutmut_12, 
        'xǁStatsǁ_calc_trimean__mutmut_13': xǁStatsǁ_calc_trimean__mutmut_13, 
        'xǁStatsǁ_calc_trimean__mutmut_14': xǁStatsǁ_calc_trimean__mutmut_14, 
        'xǁStatsǁ_calc_trimean__mutmut_15': xǁStatsǁ_calc_trimean__mutmut_15, 
        'xǁStatsǁ_calc_trimean__mutmut_16': xǁStatsǁ_calc_trimean__mutmut_16, 
        'xǁStatsǁ_calc_trimean__mutmut_17': xǁStatsǁ_calc_trimean__mutmut_17, 
        'xǁStatsǁ_calc_trimean__mutmut_18': xǁStatsǁ_calc_trimean__mutmut_18, 
        'xǁStatsǁ_calc_trimean__mutmut_19': xǁStatsǁ_calc_trimean__mutmut_19
    }
    
    def _calc_trimean(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_trimean__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_trimean__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_trimean.__signature__ = _mutmut_signature(xǁStatsǁ_calc_trimean__mutmut_orig)
    xǁStatsǁ_calc_trimean__mutmut_orig.__name__ = 'xǁStatsǁ_calc_trimean'
    trimean = _StatsProperty('trimean', _calc_trimean)

    def xǁStatsǁ_calc_variance__mutmut_orig(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        global mean  # defined elsewhere in this file
        return mean(self._get_pow_diffs(2))

    def xǁStatsǁ_calc_variance__mutmut_1(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        global mean  # defined elsewhere in this file
        return mean(None)

    def xǁStatsǁ_calc_variance__mutmut_2(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        global mean  # defined elsewhere in this file
        return mean(self._get_pow_diffs(None))

    def xǁStatsǁ_calc_variance__mutmut_3(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        global mean  # defined elsewhere in this file
        return mean(self._get_pow_diffs(3))
    
    xǁStatsǁ_calc_variance__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_variance__mutmut_1': xǁStatsǁ_calc_variance__mutmut_1, 
        'xǁStatsǁ_calc_variance__mutmut_2': xǁStatsǁ_calc_variance__mutmut_2, 
        'xǁStatsǁ_calc_variance__mutmut_3': xǁStatsǁ_calc_variance__mutmut_3
    }
    
    def _calc_variance(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_variance__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_variance__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_variance.__signature__ = _mutmut_signature(xǁStatsǁ_calc_variance__mutmut_orig)
    xǁStatsǁ_calc_variance__mutmut_orig.__name__ = 'xǁStatsǁ_calc_variance'
    variance = _StatsProperty('variance', _calc_variance)

    def xǁStatsǁ_calc_std_dev__mutmut_orig(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance ** 0.5

    def xǁStatsǁ_calc_std_dev__mutmut_1(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance * 0.5

    def xǁStatsǁ_calc_std_dev__mutmut_2(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance ** 1.5
    
    xǁStatsǁ_calc_std_dev__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_std_dev__mutmut_1': xǁStatsǁ_calc_std_dev__mutmut_1, 
        'xǁStatsǁ_calc_std_dev__mutmut_2': xǁStatsǁ_calc_std_dev__mutmut_2
    }
    
    def _calc_std_dev(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_std_dev__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_std_dev__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_std_dev.__signature__ = _mutmut_signature(xǁStatsǁ_calc_std_dev__mutmut_orig)
    xǁStatsǁ_calc_std_dev__mutmut_orig.__name__ = 'xǁStatsǁ_calc_std_dev'
    std_dev = _StatsProperty('std_dev', _calc_std_dev)

    def xǁStatsǁ_calc_median_abs_dev__mutmut_orig(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_1(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = None
        x = float(median(sorted_vals))
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_2(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(None)
        x = float(median(sorted_vals))
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_3(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = None
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_4(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(None)
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_5(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(None))
        return median([abs(x - v) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_6(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median(None)

    def xǁStatsǁ_calc_median_abs_dev__mutmut_7(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median([abs(None) for v in sorted_vals])

    def xǁStatsǁ_calc_median_abs_dev__mutmut_8(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        global median  # defined elsewhere in this file
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median([abs(x + v) for v in sorted_vals])
    
    xǁStatsǁ_calc_median_abs_dev__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_median_abs_dev__mutmut_1': xǁStatsǁ_calc_median_abs_dev__mutmut_1, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_2': xǁStatsǁ_calc_median_abs_dev__mutmut_2, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_3': xǁStatsǁ_calc_median_abs_dev__mutmut_3, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_4': xǁStatsǁ_calc_median_abs_dev__mutmut_4, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_5': xǁStatsǁ_calc_median_abs_dev__mutmut_5, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_6': xǁStatsǁ_calc_median_abs_dev__mutmut_6, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_7': xǁStatsǁ_calc_median_abs_dev__mutmut_7, 
        'xǁStatsǁ_calc_median_abs_dev__mutmut_8': xǁStatsǁ_calc_median_abs_dev__mutmut_8
    }
    
    def _calc_median_abs_dev(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_median_abs_dev__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_median_abs_dev__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_median_abs_dev.__signature__ = _mutmut_signature(xǁStatsǁ_calc_median_abs_dev__mutmut_orig)
    xǁStatsǁ_calc_median_abs_dev__mutmut_orig.__name__ = 'xǁStatsǁ_calc_median_abs_dev'
    median_abs_dev = _StatsProperty('median_abs_dev', _calc_median_abs_dev)
    mad = median_abs_dev  # convenience

    def xǁStatsǁ_calc_rel_std_dev__mutmut_orig(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default

    def xǁStatsǁ_calc_rel_std_dev__mutmut_1(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = None
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default

    def xǁStatsǁ_calc_rel_std_dev__mutmut_2(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = abs(None)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default

    def xǁStatsǁ_calc_rel_std_dev__mutmut_3(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev * abs_mean
        else:
            return self.default
    
    xǁStatsǁ_calc_rel_std_dev__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_rel_std_dev__mutmut_1': xǁStatsǁ_calc_rel_std_dev__mutmut_1, 
        'xǁStatsǁ_calc_rel_std_dev__mutmut_2': xǁStatsǁ_calc_rel_std_dev__mutmut_2, 
        'xǁStatsǁ_calc_rel_std_dev__mutmut_3': xǁStatsǁ_calc_rel_std_dev__mutmut_3
    }
    
    def _calc_rel_std_dev(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_rel_std_dev__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_rel_std_dev__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_rel_std_dev.__signature__ = _mutmut_signature(xǁStatsǁ_calc_rel_std_dev__mutmut_orig)
    xǁStatsǁ_calc_rel_std_dev__mutmut_orig.__name__ = 'xǁStatsǁ_calc_rel_std_dev'
    rel_std_dev = _StatsProperty('rel_std_dev', _calc_rel_std_dev)

    def xǁStatsǁ_calc_skewness__mutmut_orig(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_1(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = None
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_2(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 or s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_3(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) >= 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_4(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 2 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_5(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev >= 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_6(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 1:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_7(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) * float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_8(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(None) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_9(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(None)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_10(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_11(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float(None))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_12(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) / (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_13(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) + 1) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_14(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 2) * (s_dev ** 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_15(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev * 3)))
        else:
            return self.default

    def xǁStatsǁ_calc_skewness__mutmut_16(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return self.default
    
    xǁStatsǁ_calc_skewness__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_skewness__mutmut_1': xǁStatsǁ_calc_skewness__mutmut_1, 
        'xǁStatsǁ_calc_skewness__mutmut_2': xǁStatsǁ_calc_skewness__mutmut_2, 
        'xǁStatsǁ_calc_skewness__mutmut_3': xǁStatsǁ_calc_skewness__mutmut_3, 
        'xǁStatsǁ_calc_skewness__mutmut_4': xǁStatsǁ_calc_skewness__mutmut_4, 
        'xǁStatsǁ_calc_skewness__mutmut_5': xǁStatsǁ_calc_skewness__mutmut_5, 
        'xǁStatsǁ_calc_skewness__mutmut_6': xǁStatsǁ_calc_skewness__mutmut_6, 
        'xǁStatsǁ_calc_skewness__mutmut_7': xǁStatsǁ_calc_skewness__mutmut_7, 
        'xǁStatsǁ_calc_skewness__mutmut_8': xǁStatsǁ_calc_skewness__mutmut_8, 
        'xǁStatsǁ_calc_skewness__mutmut_9': xǁStatsǁ_calc_skewness__mutmut_9, 
        'xǁStatsǁ_calc_skewness__mutmut_10': xǁStatsǁ_calc_skewness__mutmut_10, 
        'xǁStatsǁ_calc_skewness__mutmut_11': xǁStatsǁ_calc_skewness__mutmut_11, 
        'xǁStatsǁ_calc_skewness__mutmut_12': xǁStatsǁ_calc_skewness__mutmut_12, 
        'xǁStatsǁ_calc_skewness__mutmut_13': xǁStatsǁ_calc_skewness__mutmut_13, 
        'xǁStatsǁ_calc_skewness__mutmut_14': xǁStatsǁ_calc_skewness__mutmut_14, 
        'xǁStatsǁ_calc_skewness__mutmut_15': xǁStatsǁ_calc_skewness__mutmut_15, 
        'xǁStatsǁ_calc_skewness__mutmut_16': xǁStatsǁ_calc_skewness__mutmut_16
    }
    
    def _calc_skewness(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_skewness__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_skewness__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_skewness.__signature__ = _mutmut_signature(xǁStatsǁ_calc_skewness__mutmut_orig)
    xǁStatsǁ_calc_skewness__mutmut_orig.__name__ = 'xǁStatsǁ_calc_skewness'
    skewness = _StatsProperty('skewness', _calc_skewness)

    def xǁStatsǁ_calc_kurtosis__mutmut_orig(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_1(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = None
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_2(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 or s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_3(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) >= 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_4(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 2 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_5(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev >= 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_6(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 1:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_7(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) * float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_8(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(None) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_9(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(None)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_10(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(5)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_11(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float(None))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_12(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) / (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_13(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) + 1) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_14(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 2) * (s_dev ** 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_15(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev * 4)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_16(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 5)))
        else:
            return 0.0

    def xǁStatsǁ_calc_kurtosis__mutmut_17(self):
        """\
        Indicates how much data is in the tails of the distribution. The
        result is always positive, with the normal "bell-curve"
        distribution having a kurtosis of 3.

        http://en.wikipedia.org/wiki/Kurtosis

        See the module docstring for more about statistical moments.

        >>> kurtosis(range(9))
        1.99125

        With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
        centrally distributed than the normal curve.
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 1.0
    
    xǁStatsǁ_calc_kurtosis__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_kurtosis__mutmut_1': xǁStatsǁ_calc_kurtosis__mutmut_1, 
        'xǁStatsǁ_calc_kurtosis__mutmut_2': xǁStatsǁ_calc_kurtosis__mutmut_2, 
        'xǁStatsǁ_calc_kurtosis__mutmut_3': xǁStatsǁ_calc_kurtosis__mutmut_3, 
        'xǁStatsǁ_calc_kurtosis__mutmut_4': xǁStatsǁ_calc_kurtosis__mutmut_4, 
        'xǁStatsǁ_calc_kurtosis__mutmut_5': xǁStatsǁ_calc_kurtosis__mutmut_5, 
        'xǁStatsǁ_calc_kurtosis__mutmut_6': xǁStatsǁ_calc_kurtosis__mutmut_6, 
        'xǁStatsǁ_calc_kurtosis__mutmut_7': xǁStatsǁ_calc_kurtosis__mutmut_7, 
        'xǁStatsǁ_calc_kurtosis__mutmut_8': xǁStatsǁ_calc_kurtosis__mutmut_8, 
        'xǁStatsǁ_calc_kurtosis__mutmut_9': xǁStatsǁ_calc_kurtosis__mutmut_9, 
        'xǁStatsǁ_calc_kurtosis__mutmut_10': xǁStatsǁ_calc_kurtosis__mutmut_10, 
        'xǁStatsǁ_calc_kurtosis__mutmut_11': xǁStatsǁ_calc_kurtosis__mutmut_11, 
        'xǁStatsǁ_calc_kurtosis__mutmut_12': xǁStatsǁ_calc_kurtosis__mutmut_12, 
        'xǁStatsǁ_calc_kurtosis__mutmut_13': xǁStatsǁ_calc_kurtosis__mutmut_13, 
        'xǁStatsǁ_calc_kurtosis__mutmut_14': xǁStatsǁ_calc_kurtosis__mutmut_14, 
        'xǁStatsǁ_calc_kurtosis__mutmut_15': xǁStatsǁ_calc_kurtosis__mutmut_15, 
        'xǁStatsǁ_calc_kurtosis__mutmut_16': xǁStatsǁ_calc_kurtosis__mutmut_16, 
        'xǁStatsǁ_calc_kurtosis__mutmut_17': xǁStatsǁ_calc_kurtosis__mutmut_17
    }
    
    def _calc_kurtosis(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_kurtosis__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_kurtosis__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_kurtosis.__signature__ = _mutmut_signature(xǁStatsǁ_calc_kurtosis__mutmut_orig)
    xǁStatsǁ_calc_kurtosis__mutmut_orig.__name__ = 'xǁStatsǁ_calc_kurtosis'
    kurtosis = _StatsProperty('kurtosis', _calc_kurtosis)

    def xǁStatsǁ_calc_pearson_type__mutmut_orig(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_1(self):
        precision = None
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_2(self):
        precision = self._pearson_precision
        skewness = None
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_3(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = None
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_4(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = None
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_5(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness * 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_6(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 3.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_7(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = None

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_8(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis / 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_9(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 2.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_10(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = None
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_11(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) + (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_12(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 / beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_13(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (5 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_14(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 / beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_15(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (4 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_16(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = None
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_17(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness / (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_18(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 - 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_19(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 4)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_20(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = None

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_21(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) + 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_22(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) + (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_23(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 / beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_24(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (3 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_25(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 / beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_26(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (4 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_27(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 7

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_28(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(None, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_29(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, None) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_30(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_31(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, ) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_32(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) != 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_33(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 1:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_34(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(None, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_35(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, None) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_36(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_37(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, ) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_38(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) != 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_39(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 4:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_40(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 1  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_41(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 <= 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_42(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 4:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_43(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 3  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_44(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 >= 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_45(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 4:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_46(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 8
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_47(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(None, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_48(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, None) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_49(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_50(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, ) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_51(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) != 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_52(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 1:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_53(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 4  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_54(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = None
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_55(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 * (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_56(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 * 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_57(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 3 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_58(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 / c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_59(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 / c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_60(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (5 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_61(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k <= 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_62(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 1:
                return 1  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_63(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 2  # Beta
        raise RuntimeError('missed a spot')

    def xǁStatsǁ_calc_pearson_type__mutmut_64(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError(None)

    def xǁStatsǁ_calc_pearson_type__mutmut_65(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('XXmissed a spotXX')

    def xǁStatsǁ_calc_pearson_type__mutmut_66(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('MISSED A SPOT')
    
    xǁStatsǁ_calc_pearson_type__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_calc_pearson_type__mutmut_1': xǁStatsǁ_calc_pearson_type__mutmut_1, 
        'xǁStatsǁ_calc_pearson_type__mutmut_2': xǁStatsǁ_calc_pearson_type__mutmut_2, 
        'xǁStatsǁ_calc_pearson_type__mutmut_3': xǁStatsǁ_calc_pearson_type__mutmut_3, 
        'xǁStatsǁ_calc_pearson_type__mutmut_4': xǁStatsǁ_calc_pearson_type__mutmut_4, 
        'xǁStatsǁ_calc_pearson_type__mutmut_5': xǁStatsǁ_calc_pearson_type__mutmut_5, 
        'xǁStatsǁ_calc_pearson_type__mutmut_6': xǁStatsǁ_calc_pearson_type__mutmut_6, 
        'xǁStatsǁ_calc_pearson_type__mutmut_7': xǁStatsǁ_calc_pearson_type__mutmut_7, 
        'xǁStatsǁ_calc_pearson_type__mutmut_8': xǁStatsǁ_calc_pearson_type__mutmut_8, 
        'xǁStatsǁ_calc_pearson_type__mutmut_9': xǁStatsǁ_calc_pearson_type__mutmut_9, 
        'xǁStatsǁ_calc_pearson_type__mutmut_10': xǁStatsǁ_calc_pearson_type__mutmut_10, 
        'xǁStatsǁ_calc_pearson_type__mutmut_11': xǁStatsǁ_calc_pearson_type__mutmut_11, 
        'xǁStatsǁ_calc_pearson_type__mutmut_12': xǁStatsǁ_calc_pearson_type__mutmut_12, 
        'xǁStatsǁ_calc_pearson_type__mutmut_13': xǁStatsǁ_calc_pearson_type__mutmut_13, 
        'xǁStatsǁ_calc_pearson_type__mutmut_14': xǁStatsǁ_calc_pearson_type__mutmut_14, 
        'xǁStatsǁ_calc_pearson_type__mutmut_15': xǁStatsǁ_calc_pearson_type__mutmut_15, 
        'xǁStatsǁ_calc_pearson_type__mutmut_16': xǁStatsǁ_calc_pearson_type__mutmut_16, 
        'xǁStatsǁ_calc_pearson_type__mutmut_17': xǁStatsǁ_calc_pearson_type__mutmut_17, 
        'xǁStatsǁ_calc_pearson_type__mutmut_18': xǁStatsǁ_calc_pearson_type__mutmut_18, 
        'xǁStatsǁ_calc_pearson_type__mutmut_19': xǁStatsǁ_calc_pearson_type__mutmut_19, 
        'xǁStatsǁ_calc_pearson_type__mutmut_20': xǁStatsǁ_calc_pearson_type__mutmut_20, 
        'xǁStatsǁ_calc_pearson_type__mutmut_21': xǁStatsǁ_calc_pearson_type__mutmut_21, 
        'xǁStatsǁ_calc_pearson_type__mutmut_22': xǁStatsǁ_calc_pearson_type__mutmut_22, 
        'xǁStatsǁ_calc_pearson_type__mutmut_23': xǁStatsǁ_calc_pearson_type__mutmut_23, 
        'xǁStatsǁ_calc_pearson_type__mutmut_24': xǁStatsǁ_calc_pearson_type__mutmut_24, 
        'xǁStatsǁ_calc_pearson_type__mutmut_25': xǁStatsǁ_calc_pearson_type__mutmut_25, 
        'xǁStatsǁ_calc_pearson_type__mutmut_26': xǁStatsǁ_calc_pearson_type__mutmut_26, 
        'xǁStatsǁ_calc_pearson_type__mutmut_27': xǁStatsǁ_calc_pearson_type__mutmut_27, 
        'xǁStatsǁ_calc_pearson_type__mutmut_28': xǁStatsǁ_calc_pearson_type__mutmut_28, 
        'xǁStatsǁ_calc_pearson_type__mutmut_29': xǁStatsǁ_calc_pearson_type__mutmut_29, 
        'xǁStatsǁ_calc_pearson_type__mutmut_30': xǁStatsǁ_calc_pearson_type__mutmut_30, 
        'xǁStatsǁ_calc_pearson_type__mutmut_31': xǁStatsǁ_calc_pearson_type__mutmut_31, 
        'xǁStatsǁ_calc_pearson_type__mutmut_32': xǁStatsǁ_calc_pearson_type__mutmut_32, 
        'xǁStatsǁ_calc_pearson_type__mutmut_33': xǁStatsǁ_calc_pearson_type__mutmut_33, 
        'xǁStatsǁ_calc_pearson_type__mutmut_34': xǁStatsǁ_calc_pearson_type__mutmut_34, 
        'xǁStatsǁ_calc_pearson_type__mutmut_35': xǁStatsǁ_calc_pearson_type__mutmut_35, 
        'xǁStatsǁ_calc_pearson_type__mutmut_36': xǁStatsǁ_calc_pearson_type__mutmut_36, 
        'xǁStatsǁ_calc_pearson_type__mutmut_37': xǁStatsǁ_calc_pearson_type__mutmut_37, 
        'xǁStatsǁ_calc_pearson_type__mutmut_38': xǁStatsǁ_calc_pearson_type__mutmut_38, 
        'xǁStatsǁ_calc_pearson_type__mutmut_39': xǁStatsǁ_calc_pearson_type__mutmut_39, 
        'xǁStatsǁ_calc_pearson_type__mutmut_40': xǁStatsǁ_calc_pearson_type__mutmut_40, 
        'xǁStatsǁ_calc_pearson_type__mutmut_41': xǁStatsǁ_calc_pearson_type__mutmut_41, 
        'xǁStatsǁ_calc_pearson_type__mutmut_42': xǁStatsǁ_calc_pearson_type__mutmut_42, 
        'xǁStatsǁ_calc_pearson_type__mutmut_43': xǁStatsǁ_calc_pearson_type__mutmut_43, 
        'xǁStatsǁ_calc_pearson_type__mutmut_44': xǁStatsǁ_calc_pearson_type__mutmut_44, 
        'xǁStatsǁ_calc_pearson_type__mutmut_45': xǁStatsǁ_calc_pearson_type__mutmut_45, 
        'xǁStatsǁ_calc_pearson_type__mutmut_46': xǁStatsǁ_calc_pearson_type__mutmut_46, 
        'xǁStatsǁ_calc_pearson_type__mutmut_47': xǁStatsǁ_calc_pearson_type__mutmut_47, 
        'xǁStatsǁ_calc_pearson_type__mutmut_48': xǁStatsǁ_calc_pearson_type__mutmut_48, 
        'xǁStatsǁ_calc_pearson_type__mutmut_49': xǁStatsǁ_calc_pearson_type__mutmut_49, 
        'xǁStatsǁ_calc_pearson_type__mutmut_50': xǁStatsǁ_calc_pearson_type__mutmut_50, 
        'xǁStatsǁ_calc_pearson_type__mutmut_51': xǁStatsǁ_calc_pearson_type__mutmut_51, 
        'xǁStatsǁ_calc_pearson_type__mutmut_52': xǁStatsǁ_calc_pearson_type__mutmut_52, 
        'xǁStatsǁ_calc_pearson_type__mutmut_53': xǁStatsǁ_calc_pearson_type__mutmut_53, 
        'xǁStatsǁ_calc_pearson_type__mutmut_54': xǁStatsǁ_calc_pearson_type__mutmut_54, 
        'xǁStatsǁ_calc_pearson_type__mutmut_55': xǁStatsǁ_calc_pearson_type__mutmut_55, 
        'xǁStatsǁ_calc_pearson_type__mutmut_56': xǁStatsǁ_calc_pearson_type__mutmut_56, 
        'xǁStatsǁ_calc_pearson_type__mutmut_57': xǁStatsǁ_calc_pearson_type__mutmut_57, 
        'xǁStatsǁ_calc_pearson_type__mutmut_58': xǁStatsǁ_calc_pearson_type__mutmut_58, 
        'xǁStatsǁ_calc_pearson_type__mutmut_59': xǁStatsǁ_calc_pearson_type__mutmut_59, 
        'xǁStatsǁ_calc_pearson_type__mutmut_60': xǁStatsǁ_calc_pearson_type__mutmut_60, 
        'xǁStatsǁ_calc_pearson_type__mutmut_61': xǁStatsǁ_calc_pearson_type__mutmut_61, 
        'xǁStatsǁ_calc_pearson_type__mutmut_62': xǁStatsǁ_calc_pearson_type__mutmut_62, 
        'xǁStatsǁ_calc_pearson_type__mutmut_63': xǁStatsǁ_calc_pearson_type__mutmut_63, 
        'xǁStatsǁ_calc_pearson_type__mutmut_64': xǁStatsǁ_calc_pearson_type__mutmut_64, 
        'xǁStatsǁ_calc_pearson_type__mutmut_65': xǁStatsǁ_calc_pearson_type__mutmut_65, 
        'xǁStatsǁ_calc_pearson_type__mutmut_66': xǁStatsǁ_calc_pearson_type__mutmut_66
    }
    
    def _calc_pearson_type(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_calc_pearson_type__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_calc_pearson_type__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calc_pearson_type.__signature__ = _mutmut_signature(xǁStatsǁ_calc_pearson_type__mutmut_orig)
    xǁStatsǁ_calc_pearson_type__mutmut_orig.__name__ = 'xǁStatsǁ_calc_pearson_type'
    pearson_type = _StatsProperty('pearson_type', _calc_pearson_type)

    @staticmethod
    def _get_quantile(sorted_data, q):
        data, n = sorted_data, len(sorted_data)
        idx = q / 1.0 * (n - 1)
        idx_f, idx_c = int(floor(idx)), int(ceil(idx))
        if idx_f == idx_c:
            return data[idx_f]
        return (data[idx_f] * (idx_c - idx)) + (data[idx_c] * (idx - idx_f))

    def xǁStatsǁget_quantile__mutmut_orig(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_1(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = None
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_2(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(None)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_3(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_4(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 1.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_5(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 < q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_6(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q < 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_7(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 2.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_8(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError(None)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_9(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' / q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_10(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('XXexpected q between 0.0 and 1.0, not %rXX' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_11(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('EXPECTED Q BETWEEN 0.0 AND 1.0, NOT %R' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_12(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), q)

    def xǁStatsǁget_quantile__mutmut_13(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(None, q)

    def xǁStatsǁget_quantile__mutmut_14(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), None)

    def xǁStatsǁget_quantile__mutmut_15(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(q)

    def xǁStatsǁget_quantile__mutmut_16(self, q):
        """Get a quantile from the dataset. Quantiles are floating point
        values between ``0.0`` and ``1.0``, with ``0.0`` representing
        the minimum value in the dataset and ``1.0`` representing the
        maximum. ``0.5`` represents the median:

        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        elif not self.data:
            return self.default
        return self._get_quantile(self._get_sorted_data(), )
    
    xǁStatsǁget_quantile__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁget_quantile__mutmut_1': xǁStatsǁget_quantile__mutmut_1, 
        'xǁStatsǁget_quantile__mutmut_2': xǁStatsǁget_quantile__mutmut_2, 
        'xǁStatsǁget_quantile__mutmut_3': xǁStatsǁget_quantile__mutmut_3, 
        'xǁStatsǁget_quantile__mutmut_4': xǁStatsǁget_quantile__mutmut_4, 
        'xǁStatsǁget_quantile__mutmut_5': xǁStatsǁget_quantile__mutmut_5, 
        'xǁStatsǁget_quantile__mutmut_6': xǁStatsǁget_quantile__mutmut_6, 
        'xǁStatsǁget_quantile__mutmut_7': xǁStatsǁget_quantile__mutmut_7, 
        'xǁStatsǁget_quantile__mutmut_8': xǁStatsǁget_quantile__mutmut_8, 
        'xǁStatsǁget_quantile__mutmut_9': xǁStatsǁget_quantile__mutmut_9, 
        'xǁStatsǁget_quantile__mutmut_10': xǁStatsǁget_quantile__mutmut_10, 
        'xǁStatsǁget_quantile__mutmut_11': xǁStatsǁget_quantile__mutmut_11, 
        'xǁStatsǁget_quantile__mutmut_12': xǁStatsǁget_quantile__mutmut_12, 
        'xǁStatsǁget_quantile__mutmut_13': xǁStatsǁget_quantile__mutmut_13, 
        'xǁStatsǁget_quantile__mutmut_14': xǁStatsǁget_quantile__mutmut_14, 
        'xǁStatsǁget_quantile__mutmut_15': xǁStatsǁget_quantile__mutmut_15, 
        'xǁStatsǁget_quantile__mutmut_16': xǁStatsǁget_quantile__mutmut_16
    }
    
    def get_quantile(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁget_quantile__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁget_quantile__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_quantile.__signature__ = _mutmut_signature(xǁStatsǁget_quantile__mutmut_orig)
    xǁStatsǁget_quantile__mutmut_orig.__name__ = 'xǁStatsǁget_quantile'

    def xǁStatsǁget_zscore__mutmut_orig(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_1(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = None
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_2(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev != 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_3(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 1:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_4(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value != mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_5(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 1
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_6(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value >= mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_7(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float(None)
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_8(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('XXinfXX')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_9(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('INF')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_10(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value <= mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_11(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float(None)
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_12(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('XX-infXX')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_13(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-INF')
        return (float(value) - mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_14(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) * self.std_dev

    def xǁStatsǁget_zscore__mutmut_15(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) + mean) / self.std_dev

    def xǁStatsǁget_zscore__mutmut_16(self, value):
        """Get the z-score for *value* in the group. If the standard deviation
        is 0, 0 inf or -inf will be returned to indicate whether the value is
        equal to, greater than or below the group's mean.
        """
        mean = self.mean
        if self.std_dev == 0:
            if value == mean:
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(None) - mean) / self.std_dev
    
    xǁStatsǁget_zscore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁget_zscore__mutmut_1': xǁStatsǁget_zscore__mutmut_1, 
        'xǁStatsǁget_zscore__mutmut_2': xǁStatsǁget_zscore__mutmut_2, 
        'xǁStatsǁget_zscore__mutmut_3': xǁStatsǁget_zscore__mutmut_3, 
        'xǁStatsǁget_zscore__mutmut_4': xǁStatsǁget_zscore__mutmut_4, 
        'xǁStatsǁget_zscore__mutmut_5': xǁStatsǁget_zscore__mutmut_5, 
        'xǁStatsǁget_zscore__mutmut_6': xǁStatsǁget_zscore__mutmut_6, 
        'xǁStatsǁget_zscore__mutmut_7': xǁStatsǁget_zscore__mutmut_7, 
        'xǁStatsǁget_zscore__mutmut_8': xǁStatsǁget_zscore__mutmut_8, 
        'xǁStatsǁget_zscore__mutmut_9': xǁStatsǁget_zscore__mutmut_9, 
        'xǁStatsǁget_zscore__mutmut_10': xǁStatsǁget_zscore__mutmut_10, 
        'xǁStatsǁget_zscore__mutmut_11': xǁStatsǁget_zscore__mutmut_11, 
        'xǁStatsǁget_zscore__mutmut_12': xǁStatsǁget_zscore__mutmut_12, 
        'xǁStatsǁget_zscore__mutmut_13': xǁStatsǁget_zscore__mutmut_13, 
        'xǁStatsǁget_zscore__mutmut_14': xǁStatsǁget_zscore__mutmut_14, 
        'xǁStatsǁget_zscore__mutmut_15': xǁStatsǁget_zscore__mutmut_15, 
        'xǁStatsǁget_zscore__mutmut_16': xǁStatsǁget_zscore__mutmut_16
    }
    
    def get_zscore(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁget_zscore__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁget_zscore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_zscore.__signature__ = _mutmut_signature(xǁStatsǁget_zscore__mutmut_orig)
    xǁStatsǁget_zscore__mutmut_orig.__name__ = 'xǁStatsǁget_zscore'

    def xǁStatsǁtrim_relative__mutmut_orig(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_1(self, amount=1.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_2(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = None
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_3(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(None)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_4(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_5(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 1.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_6(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 < trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_7(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim <= 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_8(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 1.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_9(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError(None)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_10(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r' / trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_11(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('XXexpected amount between 0.0 and 0.5, not %rXX'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_12(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('EXPECTED AMOUNT BETWEEN 0.0 AND 0.5, NOT %R'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_13(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = None
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_14(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = None
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_15(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(None)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_16(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size / trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_17(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff != 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_18(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 1.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_19(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = None
        self.clear_cache()

    def xǁStatsǁtrim_relative__mutmut_20(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        Args:
            amount (float): A value between 0.0 and 0.5 to trim off of
                each side of the data.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.

        """
        trim = float(amount)
        if not 0.0 <= trim < 0.5:
            raise ValueError('expected amount between 0.0 and 0.5, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:+size_diff]
        self.clear_cache()
    
    xǁStatsǁtrim_relative__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁtrim_relative__mutmut_1': xǁStatsǁtrim_relative__mutmut_1, 
        'xǁStatsǁtrim_relative__mutmut_2': xǁStatsǁtrim_relative__mutmut_2, 
        'xǁStatsǁtrim_relative__mutmut_3': xǁStatsǁtrim_relative__mutmut_3, 
        'xǁStatsǁtrim_relative__mutmut_4': xǁStatsǁtrim_relative__mutmut_4, 
        'xǁStatsǁtrim_relative__mutmut_5': xǁStatsǁtrim_relative__mutmut_5, 
        'xǁStatsǁtrim_relative__mutmut_6': xǁStatsǁtrim_relative__mutmut_6, 
        'xǁStatsǁtrim_relative__mutmut_7': xǁStatsǁtrim_relative__mutmut_7, 
        'xǁStatsǁtrim_relative__mutmut_8': xǁStatsǁtrim_relative__mutmut_8, 
        'xǁStatsǁtrim_relative__mutmut_9': xǁStatsǁtrim_relative__mutmut_9, 
        'xǁStatsǁtrim_relative__mutmut_10': xǁStatsǁtrim_relative__mutmut_10, 
        'xǁStatsǁtrim_relative__mutmut_11': xǁStatsǁtrim_relative__mutmut_11, 
        'xǁStatsǁtrim_relative__mutmut_12': xǁStatsǁtrim_relative__mutmut_12, 
        'xǁStatsǁtrim_relative__mutmut_13': xǁStatsǁtrim_relative__mutmut_13, 
        'xǁStatsǁtrim_relative__mutmut_14': xǁStatsǁtrim_relative__mutmut_14, 
        'xǁStatsǁtrim_relative__mutmut_15': xǁStatsǁtrim_relative__mutmut_15, 
        'xǁStatsǁtrim_relative__mutmut_16': xǁStatsǁtrim_relative__mutmut_16, 
        'xǁStatsǁtrim_relative__mutmut_17': xǁStatsǁtrim_relative__mutmut_17, 
        'xǁStatsǁtrim_relative__mutmut_18': xǁStatsǁtrim_relative__mutmut_18, 
        'xǁStatsǁtrim_relative__mutmut_19': xǁStatsǁtrim_relative__mutmut_19, 
        'xǁStatsǁtrim_relative__mutmut_20': xǁStatsǁtrim_relative__mutmut_20
    }
    
    def trim_relative(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁtrim_relative__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁtrim_relative__mutmut_mutants"), args, kwargs, self)
        return result 
    
    trim_relative.__signature__ = _mutmut_signature(xǁStatsǁtrim_relative__mutmut_orig)
    xǁStatsǁtrim_relative__mutmut_orig.__name__ = 'xǁStatsǁtrim_relative'

    def xǁStatsǁ_get_pow_diffs__mutmut_orig(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v - m) ** power for v in self.data]

    def xǁStatsǁ_get_pow_diffs__mutmut_1(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = None
        return [(v - m) ** power for v in self.data]

    def xǁStatsǁ_get_pow_diffs__mutmut_2(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v - m) * power for v in self.data]

    def xǁStatsǁ_get_pow_diffs__mutmut_3(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v + m) ** power for v in self.data]
    
    xǁStatsǁ_get_pow_diffs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_get_pow_diffs__mutmut_1': xǁStatsǁ_get_pow_diffs__mutmut_1, 
        'xǁStatsǁ_get_pow_diffs__mutmut_2': xǁStatsǁ_get_pow_diffs__mutmut_2, 
        'xǁStatsǁ_get_pow_diffs__mutmut_3': xǁStatsǁ_get_pow_diffs__mutmut_3
    }
    
    def _get_pow_diffs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_get_pow_diffs__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_get_pow_diffs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_pow_diffs.__signature__ = _mutmut_signature(xǁStatsǁ_get_pow_diffs__mutmut_orig)
    xǁStatsǁ_get_pow_diffs__mutmut_orig.__name__ = 'xǁStatsǁ_get_pow_diffs'

    def xǁStatsǁ_get_bin_bounds__mutmut_orig(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_1(self, count=None, with_max=True):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_2(self, count=None, with_max=False):
        if self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_3(self, count=None, with_max=False):
        if not self.data:
            return [1.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_4(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = None
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_5(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = None

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_6(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(None), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_7(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(None)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_8(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data <= 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_9(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 5:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_10(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_11(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = None
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_12(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = None
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_13(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) * float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_14(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data + min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_15(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(None)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_16(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = None
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_17(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data - (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_18(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx / i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_19(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(None)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_20(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is not None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_21(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = None
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_22(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(None), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_23(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(1.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_24(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(None)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_25(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(1.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_26(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = None
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_27(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) * (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_28(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 / (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_29(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 3 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_30(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 + q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_31(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data * (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_32(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 * 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_33(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (2 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_34(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 4.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_35(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = None
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_36(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(None, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_37(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, None)
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_38(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_39(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, )
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_40(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(2, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_41(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(None))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_42(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil(None)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_43(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) * dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_44(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data + min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_45(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = None
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_46(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data - (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_47(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx / i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_48(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(None)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_49(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count - 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_50(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 2)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_51(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = None
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_52(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b <= max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_53(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = None
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_54(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) * float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_55(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data + min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_56(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(None)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_57(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = None

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_58(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data - (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_59(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx / i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_60(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(None)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_61(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(None)

        return bins

    def xǁStatsǁ_get_bin_bounds__mutmut_62(self, count=None, with_max=False):
        if not self.data:
            return [0.0]  # TODO: raise?

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]
        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, int(ceil((max_data - min_data) / dx)))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]
        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(None))

        return bins
    
    xǁStatsǁ_get_bin_bounds__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁ_get_bin_bounds__mutmut_1': xǁStatsǁ_get_bin_bounds__mutmut_1, 
        'xǁStatsǁ_get_bin_bounds__mutmut_2': xǁStatsǁ_get_bin_bounds__mutmut_2, 
        'xǁStatsǁ_get_bin_bounds__mutmut_3': xǁStatsǁ_get_bin_bounds__mutmut_3, 
        'xǁStatsǁ_get_bin_bounds__mutmut_4': xǁStatsǁ_get_bin_bounds__mutmut_4, 
        'xǁStatsǁ_get_bin_bounds__mutmut_5': xǁStatsǁ_get_bin_bounds__mutmut_5, 
        'xǁStatsǁ_get_bin_bounds__mutmut_6': xǁStatsǁ_get_bin_bounds__mutmut_6, 
        'xǁStatsǁ_get_bin_bounds__mutmut_7': xǁStatsǁ_get_bin_bounds__mutmut_7, 
        'xǁStatsǁ_get_bin_bounds__mutmut_8': xǁStatsǁ_get_bin_bounds__mutmut_8, 
        'xǁStatsǁ_get_bin_bounds__mutmut_9': xǁStatsǁ_get_bin_bounds__mutmut_9, 
        'xǁStatsǁ_get_bin_bounds__mutmut_10': xǁStatsǁ_get_bin_bounds__mutmut_10, 
        'xǁStatsǁ_get_bin_bounds__mutmut_11': xǁStatsǁ_get_bin_bounds__mutmut_11, 
        'xǁStatsǁ_get_bin_bounds__mutmut_12': xǁStatsǁ_get_bin_bounds__mutmut_12, 
        'xǁStatsǁ_get_bin_bounds__mutmut_13': xǁStatsǁ_get_bin_bounds__mutmut_13, 
        'xǁStatsǁ_get_bin_bounds__mutmut_14': xǁStatsǁ_get_bin_bounds__mutmut_14, 
        'xǁStatsǁ_get_bin_bounds__mutmut_15': xǁStatsǁ_get_bin_bounds__mutmut_15, 
        'xǁStatsǁ_get_bin_bounds__mutmut_16': xǁStatsǁ_get_bin_bounds__mutmut_16, 
        'xǁStatsǁ_get_bin_bounds__mutmut_17': xǁStatsǁ_get_bin_bounds__mutmut_17, 
        'xǁStatsǁ_get_bin_bounds__mutmut_18': xǁStatsǁ_get_bin_bounds__mutmut_18, 
        'xǁStatsǁ_get_bin_bounds__mutmut_19': xǁStatsǁ_get_bin_bounds__mutmut_19, 
        'xǁStatsǁ_get_bin_bounds__mutmut_20': xǁStatsǁ_get_bin_bounds__mutmut_20, 
        'xǁStatsǁ_get_bin_bounds__mutmut_21': xǁStatsǁ_get_bin_bounds__mutmut_21, 
        'xǁStatsǁ_get_bin_bounds__mutmut_22': xǁStatsǁ_get_bin_bounds__mutmut_22, 
        'xǁStatsǁ_get_bin_bounds__mutmut_23': xǁStatsǁ_get_bin_bounds__mutmut_23, 
        'xǁStatsǁ_get_bin_bounds__mutmut_24': xǁStatsǁ_get_bin_bounds__mutmut_24, 
        'xǁStatsǁ_get_bin_bounds__mutmut_25': xǁStatsǁ_get_bin_bounds__mutmut_25, 
        'xǁStatsǁ_get_bin_bounds__mutmut_26': xǁStatsǁ_get_bin_bounds__mutmut_26, 
        'xǁStatsǁ_get_bin_bounds__mutmut_27': xǁStatsǁ_get_bin_bounds__mutmut_27, 
        'xǁStatsǁ_get_bin_bounds__mutmut_28': xǁStatsǁ_get_bin_bounds__mutmut_28, 
        'xǁStatsǁ_get_bin_bounds__mutmut_29': xǁStatsǁ_get_bin_bounds__mutmut_29, 
        'xǁStatsǁ_get_bin_bounds__mutmut_30': xǁStatsǁ_get_bin_bounds__mutmut_30, 
        'xǁStatsǁ_get_bin_bounds__mutmut_31': xǁStatsǁ_get_bin_bounds__mutmut_31, 
        'xǁStatsǁ_get_bin_bounds__mutmut_32': xǁStatsǁ_get_bin_bounds__mutmut_32, 
        'xǁStatsǁ_get_bin_bounds__mutmut_33': xǁStatsǁ_get_bin_bounds__mutmut_33, 
        'xǁStatsǁ_get_bin_bounds__mutmut_34': xǁStatsǁ_get_bin_bounds__mutmut_34, 
        'xǁStatsǁ_get_bin_bounds__mutmut_35': xǁStatsǁ_get_bin_bounds__mutmut_35, 
        'xǁStatsǁ_get_bin_bounds__mutmut_36': xǁStatsǁ_get_bin_bounds__mutmut_36, 
        'xǁStatsǁ_get_bin_bounds__mutmut_37': xǁStatsǁ_get_bin_bounds__mutmut_37, 
        'xǁStatsǁ_get_bin_bounds__mutmut_38': xǁStatsǁ_get_bin_bounds__mutmut_38, 
        'xǁStatsǁ_get_bin_bounds__mutmut_39': xǁStatsǁ_get_bin_bounds__mutmut_39, 
        'xǁStatsǁ_get_bin_bounds__mutmut_40': xǁStatsǁ_get_bin_bounds__mutmut_40, 
        'xǁStatsǁ_get_bin_bounds__mutmut_41': xǁStatsǁ_get_bin_bounds__mutmut_41, 
        'xǁStatsǁ_get_bin_bounds__mutmut_42': xǁStatsǁ_get_bin_bounds__mutmut_42, 
        'xǁStatsǁ_get_bin_bounds__mutmut_43': xǁStatsǁ_get_bin_bounds__mutmut_43, 
        'xǁStatsǁ_get_bin_bounds__mutmut_44': xǁStatsǁ_get_bin_bounds__mutmut_44, 
        'xǁStatsǁ_get_bin_bounds__mutmut_45': xǁStatsǁ_get_bin_bounds__mutmut_45, 
        'xǁStatsǁ_get_bin_bounds__mutmut_46': xǁStatsǁ_get_bin_bounds__mutmut_46, 
        'xǁStatsǁ_get_bin_bounds__mutmut_47': xǁStatsǁ_get_bin_bounds__mutmut_47, 
        'xǁStatsǁ_get_bin_bounds__mutmut_48': xǁStatsǁ_get_bin_bounds__mutmut_48, 
        'xǁStatsǁ_get_bin_bounds__mutmut_49': xǁStatsǁ_get_bin_bounds__mutmut_49, 
        'xǁStatsǁ_get_bin_bounds__mutmut_50': xǁStatsǁ_get_bin_bounds__mutmut_50, 
        'xǁStatsǁ_get_bin_bounds__mutmut_51': xǁStatsǁ_get_bin_bounds__mutmut_51, 
        'xǁStatsǁ_get_bin_bounds__mutmut_52': xǁStatsǁ_get_bin_bounds__mutmut_52, 
        'xǁStatsǁ_get_bin_bounds__mutmut_53': xǁStatsǁ_get_bin_bounds__mutmut_53, 
        'xǁStatsǁ_get_bin_bounds__mutmut_54': xǁStatsǁ_get_bin_bounds__mutmut_54, 
        'xǁStatsǁ_get_bin_bounds__mutmut_55': xǁStatsǁ_get_bin_bounds__mutmut_55, 
        'xǁStatsǁ_get_bin_bounds__mutmut_56': xǁStatsǁ_get_bin_bounds__mutmut_56, 
        'xǁStatsǁ_get_bin_bounds__mutmut_57': xǁStatsǁ_get_bin_bounds__mutmut_57, 
        'xǁStatsǁ_get_bin_bounds__mutmut_58': xǁStatsǁ_get_bin_bounds__mutmut_58, 
        'xǁStatsǁ_get_bin_bounds__mutmut_59': xǁStatsǁ_get_bin_bounds__mutmut_59, 
        'xǁStatsǁ_get_bin_bounds__mutmut_60': xǁStatsǁ_get_bin_bounds__mutmut_60, 
        'xǁStatsǁ_get_bin_bounds__mutmut_61': xǁStatsǁ_get_bin_bounds__mutmut_61, 
        'xǁStatsǁ_get_bin_bounds__mutmut_62': xǁStatsǁ_get_bin_bounds__mutmut_62
    }
    
    def _get_bin_bounds(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁ_get_bin_bounds__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁ_get_bin_bounds__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_bin_bounds.__signature__ = _mutmut_signature(xǁStatsǁ_get_bin_bounds__mutmut_orig)
    xǁStatsǁ_get_bin_bounds__mutmut_orig.__name__ = 'xǁStatsǁ_get_bin_bounds'

    def xǁStatsǁget_histogram_counts__mutmut_orig(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_1(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = None
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_2(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(None)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_3(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop(None, 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_4(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', None))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_5(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop(1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_6(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', ))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_7(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('XXbin_digitsXX', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_8(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('BIN_DIGITS', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_9(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 2))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_10(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError(None)

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_11(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' / kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_12(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('XXunexpected keyword arguments: %rXX' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_13(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('UNEXPECTED KEYWORD ARGUMENTS: %R' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_14(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_15(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = None
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_16(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = None
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_17(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(None)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_18(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = None
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_19(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(None) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_20(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError(None)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_21(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' / bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_22(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('XXbins expected integer bin count or listXX'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_23(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('BINS EXPECTED INTEGER BIN COUNT OR LIST'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_24(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     'XX of float bin boundaries, not %rXX' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_25(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' OF FLOAT BIN BOUNDARIES, NOT %R' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_26(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min <= bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_27(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[1]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_28(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = None
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_29(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] - bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_30(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = None

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_31(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(None)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_32(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = None
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_33(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 * bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_34(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 11.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_35(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = None
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_36(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) * round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_37(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(None) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_38(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b / round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_39(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = None

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_40(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(None)

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_41(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(None))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_42(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = None
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_43(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) + 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_44(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(None, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_45(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, None) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_46(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_47(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, ) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_48(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 2 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_49(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = None

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_50(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(None)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_51(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = None

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_52(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(None, 0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_53(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, None)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_54(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(0)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_55(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, )) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_56(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 1)) for i, b in enumerate(bins)]

        return bin_counts

    def xǁStatsǁget_histogram_counts__mutmut_57(self, bins=None, **kw):
        """Produces a list of ``(bin, count)`` pairs comprising a histogram of
        the Stats object's data, using fixed-width bins. See
        :meth:`Stats.format_histogram` for more details.

        Args:
            bins (int): maximum number of bins, or list of
                floating-point bin boundaries. Defaults to the output of
                Freedman's algorithm.
            bin_digits (int): Number of digits used to round down the
                bin boundaries. Defaults to 1.

        The output of this method can be stored and/or modified, and
        then passed to :func:`statsutils.format_histogram_counts` to
        achieve the same text formatting as the
        :meth:`~Stats.format_histogram` method. This can be useful for
        snapshotting over time.
        """
        bin_digits = int(kw.pop('bin_digits', 1))
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw.keys())

        if not bins:
            bins = self._get_bin_bounds()
        else:
            try:
                bin_count = int(bins)
            except TypeError:
                try:
                    bins = [float(x) for x in bins]
                except Exception:
                    raise ValueError('bins expected integer bin count or list'
                                     ' of float bin boundaries, not %r' % bins)
                if self.min < bins[0]:
                    bins = [self.min] + bins
            else:
                bins = self._get_bin_bounds(bin_count)

        # floor and ceil really should have taken ndigits, like round()
        round_factor = 10.0 ** bin_digits
        bins = [floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = Counter(idxs)

        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(None)]

        return bin_counts
    
    xǁStatsǁget_histogram_counts__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁget_histogram_counts__mutmut_1': xǁStatsǁget_histogram_counts__mutmut_1, 
        'xǁStatsǁget_histogram_counts__mutmut_2': xǁStatsǁget_histogram_counts__mutmut_2, 
        'xǁStatsǁget_histogram_counts__mutmut_3': xǁStatsǁget_histogram_counts__mutmut_3, 
        'xǁStatsǁget_histogram_counts__mutmut_4': xǁStatsǁget_histogram_counts__mutmut_4, 
        'xǁStatsǁget_histogram_counts__mutmut_5': xǁStatsǁget_histogram_counts__mutmut_5, 
        'xǁStatsǁget_histogram_counts__mutmut_6': xǁStatsǁget_histogram_counts__mutmut_6, 
        'xǁStatsǁget_histogram_counts__mutmut_7': xǁStatsǁget_histogram_counts__mutmut_7, 
        'xǁStatsǁget_histogram_counts__mutmut_8': xǁStatsǁget_histogram_counts__mutmut_8, 
        'xǁStatsǁget_histogram_counts__mutmut_9': xǁStatsǁget_histogram_counts__mutmut_9, 
        'xǁStatsǁget_histogram_counts__mutmut_10': xǁStatsǁget_histogram_counts__mutmut_10, 
        'xǁStatsǁget_histogram_counts__mutmut_11': xǁStatsǁget_histogram_counts__mutmut_11, 
        'xǁStatsǁget_histogram_counts__mutmut_12': xǁStatsǁget_histogram_counts__mutmut_12, 
        'xǁStatsǁget_histogram_counts__mutmut_13': xǁStatsǁget_histogram_counts__mutmut_13, 
        'xǁStatsǁget_histogram_counts__mutmut_14': xǁStatsǁget_histogram_counts__mutmut_14, 
        'xǁStatsǁget_histogram_counts__mutmut_15': xǁStatsǁget_histogram_counts__mutmut_15, 
        'xǁStatsǁget_histogram_counts__mutmut_16': xǁStatsǁget_histogram_counts__mutmut_16, 
        'xǁStatsǁget_histogram_counts__mutmut_17': xǁStatsǁget_histogram_counts__mutmut_17, 
        'xǁStatsǁget_histogram_counts__mutmut_18': xǁStatsǁget_histogram_counts__mutmut_18, 
        'xǁStatsǁget_histogram_counts__mutmut_19': xǁStatsǁget_histogram_counts__mutmut_19, 
        'xǁStatsǁget_histogram_counts__mutmut_20': xǁStatsǁget_histogram_counts__mutmut_20, 
        'xǁStatsǁget_histogram_counts__mutmut_21': xǁStatsǁget_histogram_counts__mutmut_21, 
        'xǁStatsǁget_histogram_counts__mutmut_22': xǁStatsǁget_histogram_counts__mutmut_22, 
        'xǁStatsǁget_histogram_counts__mutmut_23': xǁStatsǁget_histogram_counts__mutmut_23, 
        'xǁStatsǁget_histogram_counts__mutmut_24': xǁStatsǁget_histogram_counts__mutmut_24, 
        'xǁStatsǁget_histogram_counts__mutmut_25': xǁStatsǁget_histogram_counts__mutmut_25, 
        'xǁStatsǁget_histogram_counts__mutmut_26': xǁStatsǁget_histogram_counts__mutmut_26, 
        'xǁStatsǁget_histogram_counts__mutmut_27': xǁStatsǁget_histogram_counts__mutmut_27, 
        'xǁStatsǁget_histogram_counts__mutmut_28': xǁStatsǁget_histogram_counts__mutmut_28, 
        'xǁStatsǁget_histogram_counts__mutmut_29': xǁStatsǁget_histogram_counts__mutmut_29, 
        'xǁStatsǁget_histogram_counts__mutmut_30': xǁStatsǁget_histogram_counts__mutmut_30, 
        'xǁStatsǁget_histogram_counts__mutmut_31': xǁStatsǁget_histogram_counts__mutmut_31, 
        'xǁStatsǁget_histogram_counts__mutmut_32': xǁStatsǁget_histogram_counts__mutmut_32, 
        'xǁStatsǁget_histogram_counts__mutmut_33': xǁStatsǁget_histogram_counts__mutmut_33, 
        'xǁStatsǁget_histogram_counts__mutmut_34': xǁStatsǁget_histogram_counts__mutmut_34, 
        'xǁStatsǁget_histogram_counts__mutmut_35': xǁStatsǁget_histogram_counts__mutmut_35, 
        'xǁStatsǁget_histogram_counts__mutmut_36': xǁStatsǁget_histogram_counts__mutmut_36, 
        'xǁStatsǁget_histogram_counts__mutmut_37': xǁStatsǁget_histogram_counts__mutmut_37, 
        'xǁStatsǁget_histogram_counts__mutmut_38': xǁStatsǁget_histogram_counts__mutmut_38, 
        'xǁStatsǁget_histogram_counts__mutmut_39': xǁStatsǁget_histogram_counts__mutmut_39, 
        'xǁStatsǁget_histogram_counts__mutmut_40': xǁStatsǁget_histogram_counts__mutmut_40, 
        'xǁStatsǁget_histogram_counts__mutmut_41': xǁStatsǁget_histogram_counts__mutmut_41, 
        'xǁStatsǁget_histogram_counts__mutmut_42': xǁStatsǁget_histogram_counts__mutmut_42, 
        'xǁStatsǁget_histogram_counts__mutmut_43': xǁStatsǁget_histogram_counts__mutmut_43, 
        'xǁStatsǁget_histogram_counts__mutmut_44': xǁStatsǁget_histogram_counts__mutmut_44, 
        'xǁStatsǁget_histogram_counts__mutmut_45': xǁStatsǁget_histogram_counts__mutmut_45, 
        'xǁStatsǁget_histogram_counts__mutmut_46': xǁStatsǁget_histogram_counts__mutmut_46, 
        'xǁStatsǁget_histogram_counts__mutmut_47': xǁStatsǁget_histogram_counts__mutmut_47, 
        'xǁStatsǁget_histogram_counts__mutmut_48': xǁStatsǁget_histogram_counts__mutmut_48, 
        'xǁStatsǁget_histogram_counts__mutmut_49': xǁStatsǁget_histogram_counts__mutmut_49, 
        'xǁStatsǁget_histogram_counts__mutmut_50': xǁStatsǁget_histogram_counts__mutmut_50, 
        'xǁStatsǁget_histogram_counts__mutmut_51': xǁStatsǁget_histogram_counts__mutmut_51, 
        'xǁStatsǁget_histogram_counts__mutmut_52': xǁStatsǁget_histogram_counts__mutmut_52, 
        'xǁStatsǁget_histogram_counts__mutmut_53': xǁStatsǁget_histogram_counts__mutmut_53, 
        'xǁStatsǁget_histogram_counts__mutmut_54': xǁStatsǁget_histogram_counts__mutmut_54, 
        'xǁStatsǁget_histogram_counts__mutmut_55': xǁStatsǁget_histogram_counts__mutmut_55, 
        'xǁStatsǁget_histogram_counts__mutmut_56': xǁStatsǁget_histogram_counts__mutmut_56, 
        'xǁStatsǁget_histogram_counts__mutmut_57': xǁStatsǁget_histogram_counts__mutmut_57
    }
    
    def get_histogram_counts(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁget_histogram_counts__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁget_histogram_counts__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_histogram_counts.__signature__ = _mutmut_signature(xǁStatsǁget_histogram_counts__mutmut_orig)
    xǁStatsǁget_histogram_counts__mutmut_orig.__name__ = 'xǁStatsǁget_histogram_counts'

    def xǁStatsǁformat_histogram__mutmut_orig(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_1(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = None
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_2(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop(None, None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_3(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop(None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_4(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', )
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_5(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('XXwidthXX', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_6(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('WIDTH', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_7(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = None
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_8(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop(None, None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_9(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop(None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_10(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', )
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_11(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('XXformat_binXX', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_12(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('FORMAT_BIN', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_13(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = None
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_14(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=None, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_15(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(**kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_16(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, )
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_17(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(None,
                                       width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_18(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=None,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_19(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       format_bin=None)

    def xǁStatsǁformat_histogram__mutmut_20(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(width=width,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_21(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       format_bin=format_bin)

    def xǁStatsǁformat_histogram__mutmut_22(self, bins=None, **kw):
        """Produces a textual histogram of the data, using fixed-width bins,
        allowing for simple visualization, even in console environments.

        >>> data = list(range(20)) + list(range(5, 15)) + [10]
        >>> print(Stats(data).format_histogram(width=30))
         0.0:  5 #########
         4.4:  8 ###############
         8.9: 11 ####################
        13.3:  5 #########
        17.8:  2 ####

        In this histogram, five values are between 0.0 and 4.4, eight
        are between 4.4 and 8.9, and two values lie between 17.8 and
        the max.

        You can specify the number of bins, or provide a list of
        bin boundaries themselves. If no bins are provided, as in the
        example above, `Freedman's algorithm`_ for bin selection is
        used.

        Args:
            bins (int): Maximum number of bins for the
                histogram. Also accepts a list of floating-point
                bin boundaries. If the minimum boundary is still
                greater than the minimum value in the data, that
                boundary will be implicitly added. Defaults to the bin
                boundaries returned by `Freedman's algorithm`_.
            bin_digits (int): Number of digits to round each bin
                to. Note that bins are always rounded down to avoid
                clipping any data. Defaults to 1.
            width (int): integer number of columns in the longest line
               in the histogram. Defaults to console width on Python
               3.3+, or 80 if that is not available.
            format_bin (callable): Called on each bin to create a
               label for the final output. Use this function to add
               units, such as "ms" for milliseconds.

        Should you want something more programmatically reusable, see
        the :meth:`~Stats.get_histogram_counts` method, the output of
        is used by format_histogram. The :meth:`~Stats.describe`
        method is another useful summarization method, albeit less
        visual.

        .. _Freedman's algorithm: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
        """
        width = kw.pop('width', None)
        format_bin = kw.pop('format_bin', None)
        bin_counts = self.get_histogram_counts(bins=bins, **kw)
        return format_histogram_counts(bin_counts,
                                       width=width,
                                       )
    
    xǁStatsǁformat_histogram__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁformat_histogram__mutmut_1': xǁStatsǁformat_histogram__mutmut_1, 
        'xǁStatsǁformat_histogram__mutmut_2': xǁStatsǁformat_histogram__mutmut_2, 
        'xǁStatsǁformat_histogram__mutmut_3': xǁStatsǁformat_histogram__mutmut_3, 
        'xǁStatsǁformat_histogram__mutmut_4': xǁStatsǁformat_histogram__mutmut_4, 
        'xǁStatsǁformat_histogram__mutmut_5': xǁStatsǁformat_histogram__mutmut_5, 
        'xǁStatsǁformat_histogram__mutmut_6': xǁStatsǁformat_histogram__mutmut_6, 
        'xǁStatsǁformat_histogram__mutmut_7': xǁStatsǁformat_histogram__mutmut_7, 
        'xǁStatsǁformat_histogram__mutmut_8': xǁStatsǁformat_histogram__mutmut_8, 
        'xǁStatsǁformat_histogram__mutmut_9': xǁStatsǁformat_histogram__mutmut_9, 
        'xǁStatsǁformat_histogram__mutmut_10': xǁStatsǁformat_histogram__mutmut_10, 
        'xǁStatsǁformat_histogram__mutmut_11': xǁStatsǁformat_histogram__mutmut_11, 
        'xǁStatsǁformat_histogram__mutmut_12': xǁStatsǁformat_histogram__mutmut_12, 
        'xǁStatsǁformat_histogram__mutmut_13': xǁStatsǁformat_histogram__mutmut_13, 
        'xǁStatsǁformat_histogram__mutmut_14': xǁStatsǁformat_histogram__mutmut_14, 
        'xǁStatsǁformat_histogram__mutmut_15': xǁStatsǁformat_histogram__mutmut_15, 
        'xǁStatsǁformat_histogram__mutmut_16': xǁStatsǁformat_histogram__mutmut_16, 
        'xǁStatsǁformat_histogram__mutmut_17': xǁStatsǁformat_histogram__mutmut_17, 
        'xǁStatsǁformat_histogram__mutmut_18': xǁStatsǁformat_histogram__mutmut_18, 
        'xǁStatsǁformat_histogram__mutmut_19': xǁStatsǁformat_histogram__mutmut_19, 
        'xǁStatsǁformat_histogram__mutmut_20': xǁStatsǁformat_histogram__mutmut_20, 
        'xǁStatsǁformat_histogram__mutmut_21': xǁStatsǁformat_histogram__mutmut_21, 
        'xǁStatsǁformat_histogram__mutmut_22': xǁStatsǁformat_histogram__mutmut_22
    }
    
    def format_histogram(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁformat_histogram__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁformat_histogram__mutmut_mutants"), args, kwargs, self)
        return result 
    
    format_histogram.__signature__ = _mutmut_signature(xǁStatsǁformat_histogram__mutmut_orig)
    xǁStatsǁformat_histogram__mutmut_orig.__name__ = 'xǁStatsǁformat_histogram'

    def xǁStatsǁdescribe__mutmut_orig(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_1(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is not None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_2(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = None
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_3(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'XXdictXX'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_4(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'DICT'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_5(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_6(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('XXdictXX', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_7(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('DICT', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_8(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'XXlistXX', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_9(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'LIST', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_10(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'XXtextXX'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_11(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'TEXT'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_12(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError(None)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_13(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r' / format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_14(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('XXinvalid format for describe,XX'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_15(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('INVALID FORMAT FOR DESCRIBE,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_16(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             'XX expected one of "dict"/"list"/"text", not %rXX'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_17(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' EXPECTED ONE OF "DICT"/"LIST"/"TEXT", NOT %R'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_18(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = None
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_19(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles and [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_20(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [1.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_21(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 1.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_22(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 1.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_23(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = None
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_24(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = None
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_25(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(None)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_26(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append(None)

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_27(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(None), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_28(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = None

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_29(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('XXcountXX', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_30(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('COUNT', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_31(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('XXmeanXX', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_32(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('MEAN', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_33(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('XXstd_devXX', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_34(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('STD_DEV', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_35(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('XXmadXX', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_36(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('MAD', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_37(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('XXminXX', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_38(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('MIN', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_39(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(None)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_40(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(None)
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_41(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('XXmaxXX', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_42(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('MAX', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_43(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format != 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_44(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'XXdictXX':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_45(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'DICT':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_46(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = None
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_47(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(None)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_48(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format != 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_49(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'XXlistXX':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_50(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'LIST':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_51(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = None
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_52(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format != 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_53(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'XXtextXX':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_54(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'TEXT':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_55(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = None
        return ret

    def xǁStatsǁdescribe__mutmut_56(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(None)
        return ret

    def xǁStatsǁdescribe__mutmut_57(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = 'XX\nXX'.join(['{}{}'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_58(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format(None, val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_59(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), None)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_60(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format(val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_61(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(10), )
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_62(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['XX{}{}XX'.format((label + ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_63(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(None), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_64(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').rjust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_65(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label - ':').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_66(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + 'XX:XX').ljust(10), val)
                             for label, val in items])
        return ret

    def xǁStatsǁdescribe__mutmut_67(self, quantiles=None, format=None):
        """Provides standard summary statistics for the data in the Stats
        object, in one of several convenient formats.

        Args:
            quantiles (list): A list of numeric values to use as
                quantiles in the resulting summary. All values must be
                0.0-1.0, with 0.5 representing the median. Defaults to
                ``[0.25, 0.5, 0.75]``, representing the standard
                quartiles.
            format (str): Controls the return type of the function,
                with one of three valid values: ``"dict"`` gives back
                a :class:`dict` with the appropriate keys and
                values. ``"list"`` is a list of key-value pairs in an
                order suitable to pass to an OrderedDict or HTML
                table. ``"text"`` converts the values to text suitable
                for printing, as seen below.

        Here is the information returned by a default ``describe``, as
        presented in the ``"text"`` format:

        >>> stats = Stats(range(1, 8))
        >>> print(stats.describe(format='text'))
        count:    7
        mean:     4.0
        std_dev:  2.0
        mad:      2.0
        min:      1
        0.25:     2.5
        0.5:      4
        0.75:     5.5
        max:      7

        For more advanced descriptive statistics, check out my blog
        post on the topic `Statistics for Software
        <https://www.paypal-engineering.com/2016/04/11/statistics-for-software/>`_.

        """
        if format is None:
            format = 'dict'
        elif format not in ('dict', 'list', 'text'):
            raise ValueError('invalid format for describe,'
                             ' expected one of "dict"/"list"/"text", not %r'
                             % format)
        quantiles = quantiles or [0.25, 0.5, 0.75]
        q_items = []
        for q in quantiles:
            q_val = self.get_quantile(q)
            q_items.append((str(q), q_val))

        items = [('count', self.count),
                 ('mean', self.mean),
                 ('std_dev', self.std_dev),
                 ('mad', self.mad),
                 ('min', self.min)]

        items.extend(q_items)
        items.append(('max', self.max))
        if format == 'dict':
            ret = dict(items)
        elif format == 'list':
            ret = items
        elif format == 'text':
            ret = '\n'.join(['{}{}'.format((label + ':').ljust(11), val)
                             for label, val in items])
        return ret
    
    xǁStatsǁdescribe__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStatsǁdescribe__mutmut_1': xǁStatsǁdescribe__mutmut_1, 
        'xǁStatsǁdescribe__mutmut_2': xǁStatsǁdescribe__mutmut_2, 
        'xǁStatsǁdescribe__mutmut_3': xǁStatsǁdescribe__mutmut_3, 
        'xǁStatsǁdescribe__mutmut_4': xǁStatsǁdescribe__mutmut_4, 
        'xǁStatsǁdescribe__mutmut_5': xǁStatsǁdescribe__mutmut_5, 
        'xǁStatsǁdescribe__mutmut_6': xǁStatsǁdescribe__mutmut_6, 
        'xǁStatsǁdescribe__mutmut_7': xǁStatsǁdescribe__mutmut_7, 
        'xǁStatsǁdescribe__mutmut_8': xǁStatsǁdescribe__mutmut_8, 
        'xǁStatsǁdescribe__mutmut_9': xǁStatsǁdescribe__mutmut_9, 
        'xǁStatsǁdescribe__mutmut_10': xǁStatsǁdescribe__mutmut_10, 
        'xǁStatsǁdescribe__mutmut_11': xǁStatsǁdescribe__mutmut_11, 
        'xǁStatsǁdescribe__mutmut_12': xǁStatsǁdescribe__mutmut_12, 
        'xǁStatsǁdescribe__mutmut_13': xǁStatsǁdescribe__mutmut_13, 
        'xǁStatsǁdescribe__mutmut_14': xǁStatsǁdescribe__mutmut_14, 
        'xǁStatsǁdescribe__mutmut_15': xǁStatsǁdescribe__mutmut_15, 
        'xǁStatsǁdescribe__mutmut_16': xǁStatsǁdescribe__mutmut_16, 
        'xǁStatsǁdescribe__mutmut_17': xǁStatsǁdescribe__mutmut_17, 
        'xǁStatsǁdescribe__mutmut_18': xǁStatsǁdescribe__mutmut_18, 
        'xǁStatsǁdescribe__mutmut_19': xǁStatsǁdescribe__mutmut_19, 
        'xǁStatsǁdescribe__mutmut_20': xǁStatsǁdescribe__mutmut_20, 
        'xǁStatsǁdescribe__mutmut_21': xǁStatsǁdescribe__mutmut_21, 
        'xǁStatsǁdescribe__mutmut_22': xǁStatsǁdescribe__mutmut_22, 
        'xǁStatsǁdescribe__mutmut_23': xǁStatsǁdescribe__mutmut_23, 
        'xǁStatsǁdescribe__mutmut_24': xǁStatsǁdescribe__mutmut_24, 
        'xǁStatsǁdescribe__mutmut_25': xǁStatsǁdescribe__mutmut_25, 
        'xǁStatsǁdescribe__mutmut_26': xǁStatsǁdescribe__mutmut_26, 
        'xǁStatsǁdescribe__mutmut_27': xǁStatsǁdescribe__mutmut_27, 
        'xǁStatsǁdescribe__mutmut_28': xǁStatsǁdescribe__mutmut_28, 
        'xǁStatsǁdescribe__mutmut_29': xǁStatsǁdescribe__mutmut_29, 
        'xǁStatsǁdescribe__mutmut_30': xǁStatsǁdescribe__mutmut_30, 
        'xǁStatsǁdescribe__mutmut_31': xǁStatsǁdescribe__mutmut_31, 
        'xǁStatsǁdescribe__mutmut_32': xǁStatsǁdescribe__mutmut_32, 
        'xǁStatsǁdescribe__mutmut_33': xǁStatsǁdescribe__mutmut_33, 
        'xǁStatsǁdescribe__mutmut_34': xǁStatsǁdescribe__mutmut_34, 
        'xǁStatsǁdescribe__mutmut_35': xǁStatsǁdescribe__mutmut_35, 
        'xǁStatsǁdescribe__mutmut_36': xǁStatsǁdescribe__mutmut_36, 
        'xǁStatsǁdescribe__mutmut_37': xǁStatsǁdescribe__mutmut_37, 
        'xǁStatsǁdescribe__mutmut_38': xǁStatsǁdescribe__mutmut_38, 
        'xǁStatsǁdescribe__mutmut_39': xǁStatsǁdescribe__mutmut_39, 
        'xǁStatsǁdescribe__mutmut_40': xǁStatsǁdescribe__mutmut_40, 
        'xǁStatsǁdescribe__mutmut_41': xǁStatsǁdescribe__mutmut_41, 
        'xǁStatsǁdescribe__mutmut_42': xǁStatsǁdescribe__mutmut_42, 
        'xǁStatsǁdescribe__mutmut_43': xǁStatsǁdescribe__mutmut_43, 
        'xǁStatsǁdescribe__mutmut_44': xǁStatsǁdescribe__mutmut_44, 
        'xǁStatsǁdescribe__mutmut_45': xǁStatsǁdescribe__mutmut_45, 
        'xǁStatsǁdescribe__mutmut_46': xǁStatsǁdescribe__mutmut_46, 
        'xǁStatsǁdescribe__mutmut_47': xǁStatsǁdescribe__mutmut_47, 
        'xǁStatsǁdescribe__mutmut_48': xǁStatsǁdescribe__mutmut_48, 
        'xǁStatsǁdescribe__mutmut_49': xǁStatsǁdescribe__mutmut_49, 
        'xǁStatsǁdescribe__mutmut_50': xǁStatsǁdescribe__mutmut_50, 
        'xǁStatsǁdescribe__mutmut_51': xǁStatsǁdescribe__mutmut_51, 
        'xǁStatsǁdescribe__mutmut_52': xǁStatsǁdescribe__mutmut_52, 
        'xǁStatsǁdescribe__mutmut_53': xǁStatsǁdescribe__mutmut_53, 
        'xǁStatsǁdescribe__mutmut_54': xǁStatsǁdescribe__mutmut_54, 
        'xǁStatsǁdescribe__mutmut_55': xǁStatsǁdescribe__mutmut_55, 
        'xǁStatsǁdescribe__mutmut_56': xǁStatsǁdescribe__mutmut_56, 
        'xǁStatsǁdescribe__mutmut_57': xǁStatsǁdescribe__mutmut_57, 
        'xǁStatsǁdescribe__mutmut_58': xǁStatsǁdescribe__mutmut_58, 
        'xǁStatsǁdescribe__mutmut_59': xǁStatsǁdescribe__mutmut_59, 
        'xǁStatsǁdescribe__mutmut_60': xǁStatsǁdescribe__mutmut_60, 
        'xǁStatsǁdescribe__mutmut_61': xǁStatsǁdescribe__mutmut_61, 
        'xǁStatsǁdescribe__mutmut_62': xǁStatsǁdescribe__mutmut_62, 
        'xǁStatsǁdescribe__mutmut_63': xǁStatsǁdescribe__mutmut_63, 
        'xǁStatsǁdescribe__mutmut_64': xǁStatsǁdescribe__mutmut_64, 
        'xǁStatsǁdescribe__mutmut_65': xǁStatsǁdescribe__mutmut_65, 
        'xǁStatsǁdescribe__mutmut_66': xǁStatsǁdescribe__mutmut_66, 
        'xǁStatsǁdescribe__mutmut_67': xǁStatsǁdescribe__mutmut_67
    }
    
    def describe(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStatsǁdescribe__mutmut_orig"), object.__getattribute__(self, "xǁStatsǁdescribe__mutmut_mutants"), args, kwargs, self)
        return result 
    
    describe.__signature__ = _mutmut_signature(xǁStatsǁdescribe__mutmut_orig)
    xǁStatsǁdescribe__mutmut_orig.__name__ = 'xǁStatsǁdescribe'


def x_describe__mutmut_orig(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(quantiles=quantiles, format=format)


def x_describe__mutmut_1(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(quantiles=None, format=format)


def x_describe__mutmut_2(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(quantiles=quantiles, format=None)


def x_describe__mutmut_3(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(format=format)


def x_describe__mutmut_4(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(data).describe(quantiles=quantiles, )


def x_describe__mutmut_5(data, quantiles=None, format=None):
    """A convenience function to get standard summary statistics useful
    for describing most data. See :meth:`Stats.describe` for more
    details.

    >>> print(describe(range(7), format='text'))
    count:    7
    mean:     3.0
    std_dev:  2.0
    mad:      2.0
    min:      0
    0.25:     1.5
    0.5:      3
    0.75:     4.5
    max:      6

    See :meth:`Stats.format_histogram` for another very useful
    summarization that uses textual visualization.
    """
    return Stats(None).describe(quantiles=quantiles, format=format)

x_describe__mutmut_mutants : ClassVar[MutantDict] = {
'x_describe__mutmut_1': x_describe__mutmut_1, 
    'x_describe__mutmut_2': x_describe__mutmut_2, 
    'x_describe__mutmut_3': x_describe__mutmut_3, 
    'x_describe__mutmut_4': x_describe__mutmut_4, 
    'x_describe__mutmut_5': x_describe__mutmut_5
}

def describe(*args, **kwargs):
    result = _mutmut_trampoline(x_describe__mutmut_orig, x_describe__mutmut_mutants, args, kwargs)
    return result 

describe.__signature__ = _mutmut_signature(x_describe__mutmut_orig)
x_describe__mutmut_orig.__name__ = 'x_describe'


def x__get_conv_func__mutmut_orig(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_1(attr_name):
    def stats_helper(data, default=1.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_2(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(None,
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_3(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       None)
    return stats_helper


def x__get_conv_func__mutmut_4(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(attr_name)
    return stats_helper


def x__get_conv_func__mutmut_5(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       )
    return stats_helper


def x__get_conv_func__mutmut_6(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(None, default=default, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_7(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=None, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_8(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=None),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_9(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(default=default, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_10(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, use_copy=False),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_11(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, ),
                       attr_name)
    return stats_helper


def x__get_conv_func__mutmut_12(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=True),
                       attr_name)
    return stats_helper

x__get_conv_func__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_conv_func__mutmut_1': x__get_conv_func__mutmut_1, 
    'x__get_conv_func__mutmut_2': x__get_conv_func__mutmut_2, 
    'x__get_conv_func__mutmut_3': x__get_conv_func__mutmut_3, 
    'x__get_conv_func__mutmut_4': x__get_conv_func__mutmut_4, 
    'x__get_conv_func__mutmut_5': x__get_conv_func__mutmut_5, 
    'x__get_conv_func__mutmut_6': x__get_conv_func__mutmut_6, 
    'x__get_conv_func__mutmut_7': x__get_conv_func__mutmut_7, 
    'x__get_conv_func__mutmut_8': x__get_conv_func__mutmut_8, 
    'x__get_conv_func__mutmut_9': x__get_conv_func__mutmut_9, 
    'x__get_conv_func__mutmut_10': x__get_conv_func__mutmut_10, 
    'x__get_conv_func__mutmut_11': x__get_conv_func__mutmut_11, 
    'x__get_conv_func__mutmut_12': x__get_conv_func__mutmut_12
}

def _get_conv_func(*args, **kwargs):
    result = _mutmut_trampoline(x__get_conv_func__mutmut_orig, x__get_conv_func__mutmut_mutants, args, kwargs)
    return result 

_get_conv_func.__signature__ = _mutmut_signature(x__get_conv_func__mutmut_orig)
x__get_conv_func__mutmut_orig.__name__ = 'x__get_conv_func'


for attr_name, attr in list(Stats.__dict__.items()):
    if isinstance(attr, _StatsProperty):
        if attr_name in ('max', 'min', 'count'):  # don't shadow builtins
            continue
        if attr_name in ('mad',):  # convenience aliases
            continue
        func = _get_conv_func(attr_name)
        func.__doc__ = attr.func.__doc__
        globals()[attr_name] = func
        delattr(Stats, '_calc_' + attr_name)
# cleanup
del attr
del attr_name
del func


def x_format_histogram_counts__mutmut_orig(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_1(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = None
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_2(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_3(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = None
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_4(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: None
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_5(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_6(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = None
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_7(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[1]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_8(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = None

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_9(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 81

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_10(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = None
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_11(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = None
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_12(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max(None)
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_13(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = None

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_14(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = None
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_15(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' / format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_16(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['XX%sXX' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_17(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%S' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_18(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(None) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_19(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = None
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_20(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max(None)
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_21(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = None

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_22(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format(None, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_23(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, None)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_24(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format(count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_25(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, )

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_26(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = 'XX{}: {} #XX'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_27(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' / label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_28(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('XXxXX' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_29(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('X' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_30(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = None
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_31(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(None, 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_32(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), None)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_33(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_34(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), )
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_35(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width + len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_36(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 4)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_37(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = None
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_38(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) * count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_39(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(None) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_40(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = None
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_41(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "XX{label:>{label_cols}}: {count:>{count_cols}} {bar}XX"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_42(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{LABEL:>{LABEL_COLS}}: {COUNT:>{COUNT_COLS}} {BAR}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_43(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(None, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_44(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, None):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_45(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_46(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, ):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_47(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = None
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_48(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(None)
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_49(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(None))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_50(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count / line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_51(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = None
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_52(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) and '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_53(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' / bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_54(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('XX#XX' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_55(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or 'XX|XX'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_56(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = None
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_57(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=None,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_58(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=None,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_59(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=None,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_60(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=None,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_61(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=None)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_62(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_63(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_64(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_65(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           bar=bar)
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_66(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           )
        lines.append(line)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_67(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(None)

    return '\n'.join(lines)


def x_format_histogram_counts__mutmut_68(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return '\n'.join(None)


def x_format_histogram_counts__mutmut_69(bin_counts, width=None, format_bin=None):
    """The formatting logic behind :meth:`Stats.format_histogram`, which
    takes the output of :meth:`Stats.get_histogram_counts`, and passes
    them to this function.

    Args:
        bin_counts (list): A list of bin values to counts.
        width (int): Number of character columns in the text output,
            defaults to 80 or console width in Python 3.3+.
        format_bin (callable): Used to convert bin values into string
            labels.
    """
    lines = []
    if not format_bin:
        format_bin = lambda v: v
    if not width:
        try:
            import shutil  # python 3 convenience
            width = shutil.get_terminal_size()[0]
        except Exception:
            width = 80

    bins = [b for b, _ in bin_counts]
    count_max = max([count for _, count in bin_counts])
    count_cols = len(str(count_max))

    labels = ['%s' % format_bin(b) for b in bins]
    label_cols = max([len(l) for l in labels])
    tmp_line = '{}: {} #'.format('x' * label_cols, count_max)

    bar_cols = max(width - len(tmp_line), 3)
    line_k = float(bar_cols) / count_max
    tmpl = "{label:>{label_cols}}: {count:>{count_cols}} {bar}"
    for label, (bin_val, count) in zip(labels, bin_counts):
        bar_len = int(round(count * line_k))
        bar = ('#' * bar_len) or '|'
        line = tmpl.format(label=label,
                           label_cols=label_cols,
                           count=count,
                           count_cols=count_cols,
                           bar=bar)
        lines.append(line)

    return 'XX\nXX'.join(lines)

x_format_histogram_counts__mutmut_mutants : ClassVar[MutantDict] = {
'x_format_histogram_counts__mutmut_1': x_format_histogram_counts__mutmut_1, 
    'x_format_histogram_counts__mutmut_2': x_format_histogram_counts__mutmut_2, 
    'x_format_histogram_counts__mutmut_3': x_format_histogram_counts__mutmut_3, 
    'x_format_histogram_counts__mutmut_4': x_format_histogram_counts__mutmut_4, 
    'x_format_histogram_counts__mutmut_5': x_format_histogram_counts__mutmut_5, 
    'x_format_histogram_counts__mutmut_6': x_format_histogram_counts__mutmut_6, 
    'x_format_histogram_counts__mutmut_7': x_format_histogram_counts__mutmut_7, 
    'x_format_histogram_counts__mutmut_8': x_format_histogram_counts__mutmut_8, 
    'x_format_histogram_counts__mutmut_9': x_format_histogram_counts__mutmut_9, 
    'x_format_histogram_counts__mutmut_10': x_format_histogram_counts__mutmut_10, 
    'x_format_histogram_counts__mutmut_11': x_format_histogram_counts__mutmut_11, 
    'x_format_histogram_counts__mutmut_12': x_format_histogram_counts__mutmut_12, 
    'x_format_histogram_counts__mutmut_13': x_format_histogram_counts__mutmut_13, 
    'x_format_histogram_counts__mutmut_14': x_format_histogram_counts__mutmut_14, 
    'x_format_histogram_counts__mutmut_15': x_format_histogram_counts__mutmut_15, 
    'x_format_histogram_counts__mutmut_16': x_format_histogram_counts__mutmut_16, 
    'x_format_histogram_counts__mutmut_17': x_format_histogram_counts__mutmut_17, 
    'x_format_histogram_counts__mutmut_18': x_format_histogram_counts__mutmut_18, 
    'x_format_histogram_counts__mutmut_19': x_format_histogram_counts__mutmut_19, 
    'x_format_histogram_counts__mutmut_20': x_format_histogram_counts__mutmut_20, 
    'x_format_histogram_counts__mutmut_21': x_format_histogram_counts__mutmut_21, 
    'x_format_histogram_counts__mutmut_22': x_format_histogram_counts__mutmut_22, 
    'x_format_histogram_counts__mutmut_23': x_format_histogram_counts__mutmut_23, 
    'x_format_histogram_counts__mutmut_24': x_format_histogram_counts__mutmut_24, 
    'x_format_histogram_counts__mutmut_25': x_format_histogram_counts__mutmut_25, 
    'x_format_histogram_counts__mutmut_26': x_format_histogram_counts__mutmut_26, 
    'x_format_histogram_counts__mutmut_27': x_format_histogram_counts__mutmut_27, 
    'x_format_histogram_counts__mutmut_28': x_format_histogram_counts__mutmut_28, 
    'x_format_histogram_counts__mutmut_29': x_format_histogram_counts__mutmut_29, 
    'x_format_histogram_counts__mutmut_30': x_format_histogram_counts__mutmut_30, 
    'x_format_histogram_counts__mutmut_31': x_format_histogram_counts__mutmut_31, 
    'x_format_histogram_counts__mutmut_32': x_format_histogram_counts__mutmut_32, 
    'x_format_histogram_counts__mutmut_33': x_format_histogram_counts__mutmut_33, 
    'x_format_histogram_counts__mutmut_34': x_format_histogram_counts__mutmut_34, 
    'x_format_histogram_counts__mutmut_35': x_format_histogram_counts__mutmut_35, 
    'x_format_histogram_counts__mutmut_36': x_format_histogram_counts__mutmut_36, 
    'x_format_histogram_counts__mutmut_37': x_format_histogram_counts__mutmut_37, 
    'x_format_histogram_counts__mutmut_38': x_format_histogram_counts__mutmut_38, 
    'x_format_histogram_counts__mutmut_39': x_format_histogram_counts__mutmut_39, 
    'x_format_histogram_counts__mutmut_40': x_format_histogram_counts__mutmut_40, 
    'x_format_histogram_counts__mutmut_41': x_format_histogram_counts__mutmut_41, 
    'x_format_histogram_counts__mutmut_42': x_format_histogram_counts__mutmut_42, 
    'x_format_histogram_counts__mutmut_43': x_format_histogram_counts__mutmut_43, 
    'x_format_histogram_counts__mutmut_44': x_format_histogram_counts__mutmut_44, 
    'x_format_histogram_counts__mutmut_45': x_format_histogram_counts__mutmut_45, 
    'x_format_histogram_counts__mutmut_46': x_format_histogram_counts__mutmut_46, 
    'x_format_histogram_counts__mutmut_47': x_format_histogram_counts__mutmut_47, 
    'x_format_histogram_counts__mutmut_48': x_format_histogram_counts__mutmut_48, 
    'x_format_histogram_counts__mutmut_49': x_format_histogram_counts__mutmut_49, 
    'x_format_histogram_counts__mutmut_50': x_format_histogram_counts__mutmut_50, 
    'x_format_histogram_counts__mutmut_51': x_format_histogram_counts__mutmut_51, 
    'x_format_histogram_counts__mutmut_52': x_format_histogram_counts__mutmut_52, 
    'x_format_histogram_counts__mutmut_53': x_format_histogram_counts__mutmut_53, 
    'x_format_histogram_counts__mutmut_54': x_format_histogram_counts__mutmut_54, 
    'x_format_histogram_counts__mutmut_55': x_format_histogram_counts__mutmut_55, 
    'x_format_histogram_counts__mutmut_56': x_format_histogram_counts__mutmut_56, 
    'x_format_histogram_counts__mutmut_57': x_format_histogram_counts__mutmut_57, 
    'x_format_histogram_counts__mutmut_58': x_format_histogram_counts__mutmut_58, 
    'x_format_histogram_counts__mutmut_59': x_format_histogram_counts__mutmut_59, 
    'x_format_histogram_counts__mutmut_60': x_format_histogram_counts__mutmut_60, 
    'x_format_histogram_counts__mutmut_61': x_format_histogram_counts__mutmut_61, 
    'x_format_histogram_counts__mutmut_62': x_format_histogram_counts__mutmut_62, 
    'x_format_histogram_counts__mutmut_63': x_format_histogram_counts__mutmut_63, 
    'x_format_histogram_counts__mutmut_64': x_format_histogram_counts__mutmut_64, 
    'x_format_histogram_counts__mutmut_65': x_format_histogram_counts__mutmut_65, 
    'x_format_histogram_counts__mutmut_66': x_format_histogram_counts__mutmut_66, 
    'x_format_histogram_counts__mutmut_67': x_format_histogram_counts__mutmut_67, 
    'x_format_histogram_counts__mutmut_68': x_format_histogram_counts__mutmut_68, 
    'x_format_histogram_counts__mutmut_69': x_format_histogram_counts__mutmut_69
}

def format_histogram_counts(*args, **kwargs):
    result = _mutmut_trampoline(x_format_histogram_counts__mutmut_orig, x_format_histogram_counts__mutmut_mutants, args, kwargs)
    return result 

format_histogram_counts.__signature__ = _mutmut_signature(x_format_histogram_counts__mutmut_orig)
x_format_histogram_counts__mutmut_orig.__name__ = 'x_format_histogram_counts'
